"""Tests: python -m unittest discover tests"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kalodata_sniper.config import Config
from kalodata_sniper.models import Product
from kalodata_sniper.scoring import (apply_filters, compute_momentum, run_scoring,
                                     score_product, select_alerts)
from kalodata_sniper.sources.api_source import (BudgetExceeded, KalodataAPIError,
                                                 KalodataClient, RateLimiter, ResponseCache,
                                                 _raise_for_api_error, extract_records,
                                                 flatten, normalise_date_range,
                                                 validate_common)
from kalodata_sniper.sources.csv_source import load_from_text, load_products, map_headers
from kalodata_sniper.state import State
from kalodata_sniper.util import parse_date, parse_number, parse_percent


class TestParsing(unittest.TestCase):
    def test_number_formats(self):
        cases = {
            "$1.2M": 1_200_000.0, "12,3 K": 12_300.0, "1.234,56": 1234.56,
            "1,234": 1234.0, "45%": 0.45, "$0": 0.0, "(500)": -500.0,
            "2.5B": 2_500_000_000.0, "": None, "n/a": None, "-": None,
        }
        for raw, expected in cases.items():
            self.assertEqual(parse_number(raw), expected, msg=raw)

    def test_percent_normalised_to_fraction(self):
        self.assertAlmostEqual(parse_percent("45%"), 0.45)
        self.assertAlmostEqual(parse_percent("45"), 0.45)
        self.assertAlmostEqual(parse_percent(0.45), 0.45)
        self.assertAlmostEqual(parse_percent("0.2"), 0.2)

    def test_dates(self):
        self.assertEqual(parse_date("2026-03-01"), date(2026, 3, 1))
        self.assertEqual(parse_date("01.03.2026"), date(2026, 3, 1))
        self.assertIsNone(parse_date("irgendwas"))


class TestHeaderMapping(unittest.TestCase):
    def test_english_headers(self):
        mapping = map_headers(["Product Name", "Revenue", "Commission Rate", "Items Sold"])
        self.assertEqual(set(mapping.values()),
                         {"name", "revenue", "commission_rate", "units_sold"})

    def test_german_headers(self):
        mapping = map_headers(["Produktname", "Umsatz", "Provision", "Kategorie"])
        self.assertEqual(set(mapping.values()), {"name", "revenue", "commission_rate", "category"})

    def test_camel_case_api_fields(self):
        mapping = map_headers(["productName", "commissionRate", "itemSold"])
        self.assertEqual(set(mapping.values()), {"name", "commission_rate", "units_sold"})

    def test_partial_match(self):
        mapping = map_headers(["Product Name", "Revenue last 7 days"])
        self.assertEqual(mapping["Revenue last 7 days"], "revenue")

    def test_unknown_headers_are_ignored_not_fatal(self):
        mapping = map_headers(["Product Name", "Voellig unbekannte Spalte"])
        self.assertEqual(list(mapping.values()), ["name"])


CSV_SAMPLE = """Product Name,Category,Price,Revenue,Items Sold,Commission Rate,Creators,Rating
Sunset Lamp,Home,"$24.99","$412,000","16,500",25%,86,4.8
Cheap Junk,Home,"$1.50","$800","530",3%,900,3.2
"""


class TestCsvSource(unittest.TestCase):
    def test_load_and_derive(self):
        products = load_from_text(CSV_SAMPLE)
        self.assertEqual(len(products), 2)
        first = products[0]
        self.assertEqual(first.name, "Sunset Lamp")
        self.assertAlmostEqual(first.price, 24.99)
        self.assertAlmostEqual(first.revenue, 412_000)
        self.assertAlmostEqual(first.commission_rate, 0.25)
        self.assertAlmostEqual(first.payout_per_sale, 24.99 * 0.25)

    def test_price_derived_from_revenue(self):
        products = load_from_text("Product Name,Revenue,Items Sold\nX,1000,50\n")
        self.assertAlmostEqual(products[0].price, 20.0)

    def test_missing_name_column_raises(self):
        with self.assertRaises(ValueError):
            load_from_text("Revenue,Price\n100,10\n")

    def test_semicolon_delimiter(self):
        products = load_from_text("Produktname;Umsatz;Preis\nTest;1.234,50;9,99\n")
        self.assertEqual(products[0].name, "Test")
        self.assertAlmostEqual(products[0].revenue, 1234.50)


class TestRealApiFieldNames(unittest.TestCase):
    """Feldnamen aus der Kalodata-Doku - inklusive ihres Tippfehlers 'sales_volumn'."""

    API_RECORD = {
        "product_id": "123", "product_title": "LED Lampe", "product_number": 5,
        "revenue": 2500.75, "sales_volumn": 45, "views": 150000, "product_gpm": 16.67,
        "creator_number": 42, "video_number": 180, "commission_rate": 0.25,
        "avg_price": 24.99, "category_name": "Home", "revenue_trend": [50000, 62000],
        "belonged_creator_handle": "techreviewer",
    }

    def test_mapping_of_api_fields(self):
        mapping = map_headers(self.API_RECORD.keys())
        self.assertEqual(mapping["product_title"], "name")
        self.assertEqual(mapping["sales_volumn"], "units_sold")
        self.assertEqual(mapping["product_gpm"], "gpm")
        self.assertEqual(mapping["creator_number"], "creators")
        self.assertEqual(mapping["revenue_trend"], "revenue_series")

    def test_ambiguous_fields_stay_unmapped(self):
        """product_number ist die Anzahl Produkte im Video - nicht der Produktname."""
        mapping = map_headers(self.API_RECORD.keys())
        self.assertNotIn("product_number", mapping)
        self.assertNotIn("belonged_creator_handle", mapping)

    def test_exact_match_wins_over_partial(self):
        mapping = map_headers(["product_number", "product_title"])
        self.assertEqual(mapping["product_title"], "name")
        self.assertNotIn("product_number", mapping)

    def test_full_record_becomes_product(self):
        product = load_products([flatten(self.API_RECORD)])[0]
        self.assertEqual(product.name, "LED Lampe")
        self.assertEqual(product.units_sold, 45)
        self.assertEqual(product.creators, 42)
        self.assertEqual(product.revenue_series, [50000.0, 62000.0])
        self.assertAlmostEqual(product.trend_momentum, 0.24)


class TestTrendMomentum(unittest.TestCase):
    def test_second_half_against_first(self):
        self.assertAlmostEqual(Product(name="x", revenue_series=[50000, 62000]).trend_momentum, 0.24)
        self.assertAlmostEqual(
            Product(name="x", revenue_series=[100, 100, 100, 200, 200, 200]).trend_momentum, 1.0)

    def test_uneven_series_is_length_normalised(self):
        # 3 Tage flach, dann 2 Tage doppelt - ohne Normierung waere das verzerrt
        value = Product(name="x", revenue_series=[100, 100, 100, 200, 200]).trend_momentum
        self.assertGreater(value, 0.5)

    def test_too_short_or_zero_series(self):
        self.assertIsNone(Product(name="x", revenue_series=[100]).trend_momentum)
        self.assertIsNone(Product(name="x", revenue_series=[0, 0, 500]).trend_momentum)
        self.assertIsNone(Product(name="x").trend_momentum)

    def test_series_beats_growth_field_but_loses_to_history(self):
        product = Product(name="x", product_id="p1", revenue=150_000,
                          revenue_series=[100, 200], revenue_growth=9.9)
        # ohne Verlauf gewinnt die Tagesreihe gegen das Exportfeld
        self.assertAlmostEqual(compute_momentum(product, None), 1.0)

        state = State(os.path.join(tempfile.mkdtemp(), "state.json"))
        old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        state.data["products"]["p1"] = {
            "first_seen": old, "last_seen": old,
            "history": [{"ts": old, "revenue": 100_000, "score": 40}]}
        # mit Verlauf gewinnt der Snapshot-Vergleich
        self.assertAlmostEqual(compute_momentum(product, state), 0.5)

    def test_series_from_csv_string(self):
        products = load_from_text("Product Name,Revenue,Revenue Trend\nX,1000,\"50000,62000\"\n")
        self.assertEqual(products[0].revenue_series, [50000.0, 62000.0])


class TestGermanMarketDefaults(unittest.TestCase):
    def test_region_and_currency(self):
        config = Config()
        self.assertEqual(config.get("source.api.request.region"), "DE")
        self.assertEqual(config.get("source.api.request.currency"), "EUR")
        self.assertEqual(config.get("output.currency"), "\u20ac")

    def test_german_language_is_not_offered_by_the_api(self):
        """Belegt bewusst die Einschraenkung: de-DE gibt es nicht, en-US ist der Fallback."""
        from kalodata_sniper.sources.api_source import LANGUAGES
        self.assertNotIn("de-DE", LANGUAGES)
        self.assertEqual(Config().get("source.api.request.language"), "en-US")

    def test_region_override_reaches_the_request(self):
        import argparse
        from kalodata_sniper.cli import apply_request_overrides
        config = Config()
        args = argparse.Namespace(region="GB", date_range="30d", currency="USD")
        apply_request_overrides(config, args)
        self.assertEqual(config.get("source.api.request.region"), "GB")
        self.assertEqual(config.get("source.api.request.date_range"), "30d")
        self.assertEqual(config.get("output.currency"), "$")


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_good_product_passes(self):
        product = Product(name="Gut", price=25, revenue=400_000, units_sold=16_000,
                          commission_rate=0.25, rating=4.8, creators=80)
        self.assertEqual(apply_filters(product, self.config.filters), [])

    def test_low_commission_rejected(self):
        product = Product(name="Schwach", price=25, revenue=400_000, units_sold=16_000,
                          commission_rate=0.03, rating=4.8, creators=80)
        self.assertTrue(any("Provision" in r for r in apply_filters(product, self.config.filters)))

    def test_saturated_market_rejected(self):
        product = Product(name="Voll", price=25, revenue=400_000, units_sold=16_000,
                          commission_rate=0.25, rating=4.8, creators=5_000)
        self.assertTrue(any("Creator" in r for r in apply_filters(product, self.config.filters)))

    def test_keyword_blacklist(self):
        product = Product(name="Gift Card 50", price=50, revenue=90_000, units_sold=1_800,
                          commission_rate=0.2, rating=4.9, creators=10)
        self.assertTrue(any("Stichwort" in r for r in apply_filters(product, self.config.filters)))

    def test_missing_optional_data_does_not_reject(self):
        product = Product(name="Unvollstaendig", revenue=50_000)
        self.assertEqual(apply_filters(product, self.config.filters), [])

    def test_required_field_missing_rejects(self):
        product = Product(name="Ohne Umsatz", price=25)
        self.assertTrue(any("revenue" in r for r in apply_filters(product, self.config.filters)))


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_score_within_bounds(self):
        product = Product(name="X", price=25, revenue=400_000, units_sold=16_000,
                          commission_rate=0.25, rating=4.8, creators=80, revenue_growth=2.0)
        scored = score_product(product, self.config)
        self.assertGreater(scored.score, 0)
        self.assertLessEqual(scored.score, 100)

    def test_less_competition_scores_higher(self):
        base = dict(price=25, revenue=400_000, units_sold=16_000,
                    commission_rate=0.25, rating=4.8, revenue_growth=1.0)
        lean = score_product(Product(name="A", creators=20, **base), self.config)
        crowded = score_product(Product(name="B", creators=480, **base), self.config)
        self.assertGreater(lean.score, crowded.score)

    def test_missing_components_are_reweighted_not_zeroed(self):
        full = Product(name="A", price=25, revenue=400_000, commission_rate=0.25,
                       creators=20, revenue_growth=1.0)
        sparse = Product(name="B", revenue=400_000)
        self.assertNotIn("opportunity", score_product(sparse, self.config).components)
        # Ein Produkt mit fehlenden Daten faellt nicht automatisch auf 0
        self.assertGreater(score_product(sparse, self.config).score, 0)
        self.assertGreater(score_product(full, self.config).score, 0)

    def test_sorting_puts_passing_products_first(self):
        products = [
            Product(name="Rausgefiltert", price=2, revenue=500, commission_rate=0.5),
            Product(name="Guter Treffer", price=25, revenue=400_000, units_sold=16_000,
                    commission_rate=0.25, rating=4.8, creators=40, revenue_growth=2.0),
        ]
        scored = run_scoring(products, self.config)
        self.assertEqual(scored[0].product.name, "Guter Treffer")
        self.assertTrue(scored[0].passed)


class TestStateAndMomentum(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "state.json")

    def test_roundtrip(self):
        state = State(self.path)
        state.record("p1", revenue=1000, units=10, score=50, name="P1")
        state.finish_run()
        state.save()
        self.assertTrue(State(self.path).is_known("p1"))

    def test_momentum_from_older_snapshot(self):
        state = State(self.path)
        old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        state.data["products"]["p1"] = {
            "first_seen": old, "last_seen": old,
            "history": [{"ts": old, "revenue": 100_000, "units": 100, "score": 40}]}
        product = Product(name="P1", product_id="p1", revenue=150_000)
        self.assertAlmostEqual(compute_momentum(product, state), 0.5)

    def test_fresh_snapshot_does_not_kill_momentum(self):
        """Zweiter Lauf mit derselben Datei darf das Momentum nicht auf 0 setzen."""
        state = State(self.path)
        state.record("p1", revenue=150_000, units=100, score=70, name="P1")
        product = Product(name="P1", product_id="p1", revenue=150_000, revenue_growth=1.4)
        self.assertAlmostEqual(compute_momentum(product, state, lookback_hours=12), 1.4)

    def test_cooldown(self):
        state = State(self.path)
        state.mark_alerted("p1")
        self.assertTrue(state.in_cooldown("p1", 24))
        self.assertFalse(state.in_cooldown("p2", 24))

    def test_prune_removes_stale(self):
        state = State(self.path)
        ancient = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
        state.data["products"]["alt"] = {"first_seen": ancient, "last_seen": ancient, "history": []}
        state.record("neu", revenue=1, units=1, score=1)
        self.assertEqual(state.prune(120), 1)
        self.assertIn("neu", state.data["products"])

    def test_corrupt_state_file_is_recovered(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{kaputt")
        state = State(self.path)
        self.assertEqual(state.data["products"], {})
        self.assertTrue(os.path.exists(self.path + ".corrupt"))


class TestAlertSelection(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.config = Config({"alerts": {"min_score": 10, "cooldown_hours": 24,
                                         "only_new_or_rising": True, "max_per_run": 5}})
        self.state = State(os.path.join(self.dir, "state.json"))

    def _product(self, name="A"):
        return Product(name=name, product_id=name, price=25, revenue=400_000,
                       units_sold=16_000, commission_rate=0.25, rating=4.8,
                       creators=40, revenue_growth=2.0)

    def test_new_product_alerts(self):
        scored = run_scoring([self._product()], self.config, self.state)
        self.assertEqual(len(select_alerts(scored, self.config, self.state)), 1)

    def test_cooldown_suppresses_repeat(self):
        scored = run_scoring([self._product()], self.config, self.state)
        self.state.mark_alerted(scored[0].product.key)
        self.assertEqual(select_alerts(scored, self.config, self.state), [])

    def test_max_per_run(self):
        products = [self._product(f"P{i}") for i in range(20)]
        scored = run_scoring(products, self.config, self.state)
        self.assertEqual(len(select_alerts(scored, self.config, self.state)), 5)

    def test_below_min_score_never_alerts(self):
        config = Config({"alerts": {"min_score": 99.9}})
        scored = run_scoring([self._product()], config, self.state)
        self.assertEqual(select_alerts(scored, config, self.state), [])


class TestApiHelpers(unittest.TestCase):
    def test_extract_records_from_nested_payload(self):
        payload = {"code": 0, "data": {"list": [{"productName": "A"}, {"productName": "B"}]}}
        self.assertEqual(len(extract_records(payload)), 2)

    def test_extract_records_from_plain_list(self):
        self.assertEqual(len(extract_records([{"a": 1}])), 1)

    def test_extract_records_handles_garbage(self):
        self.assertEqual(extract_records({"code": 500, "msg": "error"}), [])

    def test_flatten_nested(self):
        flat = flatten({"product": {"name": "X"}, "tags": ["a", "b", "c"], "id": 7})
        self.assertEqual(flat, {"product name": "X", "tags": 3, "id": 7})

    def test_flatten_keeps_number_series(self):
        """revenue_trend darf nicht zur Laenge verdichtet werden - daraus kommt Momentum."""
        flat = flatten({"revenue_trend": [50000, 62000], "creators": [{"id": 1}, {"id": 2}]})
        self.assertEqual(flat["revenue_trend"], [50000, 62000])
        self.assertEqual(flat["creators"], 2)

    def test_detail_response_yields_single_record(self):
        payload = {"success": True, "message": "", "cached": False, "code": "",
                   "data": {"video_id": "74041", "revenue": 2500.75, "sales_volumn": 45}}
        records = extract_records(payload)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["video_id"], "74041")

    def test_envelope_only_is_not_a_record(self):
        self.assertEqual(extract_records({"success": True, "data": {}, "message": "x"}), [])

    def test_success_false_raises_with_message(self):
        with self.assertRaises(KalodataAPIError) as ctx:
            _raise_for_api_error({"success": False, "message": "invalid secret-key",
                                  "code": "AUTH_401"}, "u")
        self.assertIn("invalid secret-key", str(ctx.exception))

    def test_success_false_with_data_is_tolerated(self):
        """Die Mock-Vorschau der Doku liefert success=false trotz gefuellter Daten."""
        _raise_for_api_error({"success": False, "message": "string", "code": "string",
                              "data": {"video_id": "1", "revenue": 5}}, "u")


class TestApiClient(unittest.TestCase):
    def _client(self, **overrides):
        config = {
            "api_key": "testkey",
            "endpoints": {"rank": "/open/v1/product/rank"},
            "request": {"region": "US", "language": "en-US", "currency": "USD",
                        "date_range": "last7Day", "filters": {"min_price": 10}},
            "param_names": {"page": "page", "page_size": "page_size"},
            "cache_dir": tempfile.mkdtemp(), "cache_ttl_minutes": 0,
        }
        config.update(overrides)
        return KalodataClient(config)

    def test_missing_key_is_explicit(self):
        os.environ.pop("KALODATA_API_KEY", None)
        with self.assertRaises(KalodataAPIError) as ctx:
            KalodataClient({"endpoints": {"rank": "/x"}})
        self.assertIn("API-Key", str(ctx.exception))

    def test_auth_header_configurable(self):
        self.assertEqual(self._client()._auth_headers(), {"secret-key": "testkey"})
        custom = self._client(auth={"header": "Authorization", "prefix": "Bearer "})
        self.assertEqual(custom._auth_headers(), {"Authorization": "Bearer testkey"})

    def test_payload_carries_mandatory_fields(self):
        payload = self._client().build_payload(2)
        for field in ("region", "language", "currency", "date_range"):
            self.assertIn(field, payload)
        self.assertEqual(payload["page"], 2)
        self.assertEqual(payload["page_size"], 50)
        self.assertEqual(payload["min_price"], 10)    # Filter durchgereicht
        self.assertEqual(payload["date_range"], "last7Day")

    def test_default_base_url(self):
        self.assertEqual(self._client().base_url, "https://www.kalodata.com")

    def test_endpoint_url_from_config(self):
        client = self._client(endpoints={"rank": "/openapi/v1/tiktok/product/list"})
        self.assertEqual(client._endpoint_url("rank"),
                         "https://www.kalodata.com/openapi/v1/tiktok/product/list")

    def test_date_range_normalisation(self):
        self.assertEqual(normalise_date_range("7d"), "last7Day")
        self.assertEqual(normalise_date_range("LAST30DAY"), "last30Day")
        self.assertEqual(normalise_date_range("2026-08-01~2026-08-07"), "2026-08-01~2026-08-07")
        self.assertEqual(normalise_date_range("2026-08"), "2026-08")
        self.assertEqual(normalise_date_range(None), "last7Day")
        with self.assertRaises(KalodataAPIError):
            normalise_date_range("letzte Woche")

    def test_invalid_common_fields_are_caught_before_spending_a_request(self):
        for bad in ({"region": "XX", "language": "en-US", "currency": "USD"},
                    {"region": "US", "language": "de-DE", "currency": "USD"},
                    {"region": "US", "language": "en-US", "currency": "XYZ"}):
            with self.assertRaises(KalodataAPIError):
                validate_common(bad)
        validate_common({"region": "DE", "language": "fr-FR", "currency": "EUR"})

    def test_rate_limiter_allows_burst_then_throttles(self):
        limiter = RateLimiter(max_requests=3, window_seconds=10)
        started = time.monotonic()
        for _ in range(3):
            limiter.acquire()
        self.assertLess(time.monotonic() - started, 0.5)   # Burst laeuft ungebremst

    def test_missing_endpoint_raises_with_hint(self):
        client = self._client(endpoints={})
        with self.assertRaises(KalodataAPIError) as ctx:
            client._endpoint_url("rank")
        self.assertIn("endpoints.rank", str(ctx.exception))

    def test_budget_blocks_further_requests(self):
        client = self._client(max_requests_per_run=0)
        with self.assertRaises(BudgetExceeded):
            client.request({"page": 1})

    def test_cache_returns_without_spending_a_request(self):
        cache = ResponseCache(tempfile.mkdtemp(), ttl_minutes=60)
        cache.put("k", {"data": [{"productName": "A"}]})
        self.assertEqual(cache.get("k"), {"data": [{"productName": "A"}]})
        self.assertIsNone(ResponseCache(tempfile.mkdtemp(), 0).get("k"))

    def test_body_level_error_code_raises(self):
        with self.assertRaises(KalodataAPIError):
            _raise_for_api_error({"code": 40001, "message": "invalid param"}, "u")

    def test_success_codes_pass(self):
        for payload in ({"code": 0, "data": []}, {"code": 200}, {"status_code": "0"}):
            _raise_for_api_error(payload, "u")   # darf nicht werfen

    def test_error_code_with_data_is_tolerated(self):
        _raise_for_api_error({"code": 1, "data": [{"productName": "A"}]}, "u")


class TestPipeline(unittest.TestCase):
    def test_end_to_end_with_demo_data(self):
        from kalodata_sniper import pipeline
        from kalodata_sniper.demo import write_sample

        workdir = tempfile.mkdtemp()
        csv_path = write_sample(os.path.join(workdir, "export.csv"))
        config = Config({
            "output": {"state_file": os.path.join(workdir, "state.json"),
                       "report_dir": os.path.join(workdir, "reports")},
            "notifiers": [],
        })
        result = pipeline.run(config, input_path=csv_path, send_alerts=False, quiet=True)
        self.assertEqual(len(result.products), 15)
        self.assertTrue(result.hits)
        self.assertTrue(all(h.passed for h in result.hits))
        # Gutscheine und uebersaettigte Produkte fliegen raus
        names = [h.product.name for h in result.hits]
        self.assertNotIn("Gift Card 50 USD", names)
        self.assertNotIn("Wireless Earbuds Pro Max", names)
        # Reports und State liegen auf der Platte
        self.assertTrue(os.path.exists(os.path.join(workdir, "state.json")))
        self.assertTrue(os.path.exists(result.reports["html"]))
        with open(result.reports["html"], encoding="utf-8") as handle:
            self.assertIn("Kalodata Product Sniper", handle.read())

    def test_dry_run_writes_nothing(self):
        from kalodata_sniper import pipeline
        from kalodata_sniper.demo import write_sample

        workdir = tempfile.mkdtemp()
        csv_path = write_sample(os.path.join(workdir, "export.csv"))
        config = Config({"output": {"state_file": os.path.join(workdir, "state.json"),
                                    "report_dir": os.path.join(workdir, "reports")},
                         "notifiers": []})
        pipeline.run(config, input_path=csv_path, dry_run=True, send_alerts=False, quiet=True)
        self.assertFalse(os.path.exists(os.path.join(workdir, "state.json")))


class TestMcpServer(unittest.TestCase):
    def setUp(self):
        from kalodata_sniper.mcp_server import MCPServer
        from kalodata_sniper.demo import write_sample

        self.workdir = tempfile.mkdtemp()
        self.csv = write_sample(os.path.join(self.workdir, "export.csv"))
        config_path = os.path.join(self.workdir, "config.json")
        Config({"output": {"state_file": os.path.join(self.workdir, "state.json"),
                           "report_dir": os.path.join(self.workdir, "reports")},
                "notifiers": [{"type": "console", "enabled": True}]}).dump(config_path)
        self.server = MCPServer(config_path)

    def call(self, name, arguments=None, message_id=1):
        return self.server.handle({"jsonrpc": "2.0", "id": message_id, "method": "tools/call",
                                   "params": {"name": name, "arguments": arguments or {}}})

    def test_initialize_echoes_supported_protocol(self):
        response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                       "params": {"protocolVersion": "2024-11-05"}})
        self.assertEqual(response["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(response["result"]["serverInfo"]["name"], "kalodata-sniper")
        self.assertIn("tools", response["result"]["capabilities"])

    def test_initialize_falls_back_for_unknown_protocol(self):
        from kalodata_sniper.mcp_server import PROTOCOL_VERSION
        response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                       "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(response["result"]["protocolVersion"], PROTOCOL_VERSION)

    def test_notifications_get_no_response(self):
        self.assertIsNone(self.server.handle(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertTrue(self.server.initialized)

    def test_tools_list_schemas_are_valid(self):
        tools = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
        self.assertEqual(len(tools), 5)
        for tool in tools:
            self.assertTrue(tool["name"] and tool["description"])
            self.assertEqual(tool["inputSchema"]["type"], "object")
            for prop in tool["inputSchema"].get("properties", {}).values():
                self.assertIn("type", prop)

    def test_unknown_method_and_tool(self):
        response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "gibts/nicht"})
        self.assertEqual(response["error"]["code"], -32601)
        # Unbekannter Werkzeugname ist laut MCP-Spec ein Protokollfehler (-32602),
        # nicht ein Ergebnis mit isError - das bleibt echten Laufzeitfehlern vorbehalten.
        self.assertEqual(self.call("sniper_unsinn")["error"]["code"], -32602)

    def test_scan_returns_candidates(self):
        result = self.call("sniper_scan", {"input": self.csv, "top": 3, "dry_run": True})["result"]
        self.assertFalse(result["isError"])
        text = result["content"][0]["text"]
        self.assertIn("Kandidaten", text)
        self.assertIn("Score", text)

    def test_explain_requires_query(self):
        result = self.call("sniper_explain", {"input": self.csv})["result"]
        self.assertTrue(result["isError"])

    def test_explain_reports_filter_reason(self):
        result = self.call("sniper_explain",
                           {"query": "Gift Card", "input": self.csv})["result"]
        self.assertIn("AUSGEFILTERT", result["content"][0]["text"])

    def test_watchlist_without_history_is_helpful(self):
        text = self.call("sniper_watchlist")["result"]["content"][0]["text"]
        self.assertIn("Noch kein Verlauf", text)

    def test_watchlist_after_scan(self):
        self.call("sniper_scan", {"input": self.csv})
        text = self.call("sniper_watchlist", {"top": 5})["result"]["content"][0]["text"]
        self.assertIn("beobachtete Produkte", text)

    def test_config_tool_returns_json(self):
        payload = json.loads(self.call("sniper_config")["result"]["content"][0]["text"])
        self.assertIn("filters", payload)
        self.assertIn("weights", payload)

    def test_stdout_carries_only_protocol(self):
        """Console-Notifier aktiv: seine Ausgabe darf das Protokoll nicht zerlegen."""
        import io
        requests = "\n".join(json.dumps(m) for m in [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
             "params": {"name": "sniper_scan",
                        "arguments": {"input": self.csv, "send_alerts": True}}},
        ])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.server.serve(stdin=io.StringIO(requests), stdout=stdout)
        lines = [l for l in stdout.getvalue().split("\n") if l.strip()]
        self.assertEqual(len(lines), 2)              # Notification bleibt unbeantwortet
        for line in lines:
            json.loads(line)                          # jede Zeile ist valides JSON-RPC

    def test_missing_config_falls_back_to_defaults(self):
        """Eine fehlende Config darf nicht jeden Werkzeugaufruf toeten."""
        from kalodata_sniper.mcp_server import MCPServer
        server = MCPServer(os.path.join(self.workdir, "gibtsnicht.json"))
        response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                  "params": {"name": "sniper_config", "arguments": {}}})
        result = response["result"]
        self.assertFalse(result["isError"])
        text = result["content"][0]["text"]
        self.assertIn("Standardwerte", text)
        self.assertIn("filters", text)

    def test_malformed_json_gets_parse_error(self):
        import io
        stdout = io.StringIO()
        self.server.serve(stdin=io.StringIO("{kaputt\n"), stdout=stdout)
        self.assertEqual(json.loads(stdout.getvalue())["error"]["code"], -32700)


class TestConfig(unittest.TestCase):
    def test_deep_merge_keeps_defaults(self):
        config = Config({"filters": {"price_min": 99}})
        self.assertEqual(config.get("filters.price_min"), 99)
        self.assertEqual(config.get("filters.price_max"), 150.0)

    def test_dotted_get_with_default(self):
        self.assertEqual(Config().get("gibt.es.nicht", "fallback"), "fallback")

    def test_zero_weights_are_dropped(self):
        config = Config({"weights": {"freshness": 0}})
        self.assertNotIn("freshness", config.weights)

    def test_dump_and_reload(self):
        path = os.path.join(tempfile.mkdtemp(), "config.json")
        Config({"filters": {"price_min": 42}}).dump(path)
        self.assertEqual(Config.load(path).get("filters.price_min"), 42)


if __name__ == "__main__":
    unittest.main(verbosity=2)

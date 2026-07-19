const BASE_URL = "https://api.quiverquant.com/beta";

export class QuiverApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly path: string,
    body: string,
  ) {
    super(`QuiverQuantitative API error ${status} on ${path}: ${body}`);
    this.name = "QuiverApiError";
  }
}

export interface QuiverClientOptions {
  /** Defaults to process.env.QUIVER_API_KEY */
  apiKey?: string;
}

/**
 * Client for the QuiverQuantitative alternative-data API
 * (https://api.quiverquant.com/docs/). Auth is a Bearer token,
 * obtained from https://www.quiverquant.com/api/.
 */
export class QuiverClient {
  private readonly apiKey: string;

  constructor(options: QuiverClientOptions = {}) {
    const apiKey = options.apiKey ?? process.env.QUIVER_API_KEY;
    if (!apiKey) {
      throw new Error(
        "Missing QuiverQuantitative API key: pass { apiKey } or set QUIVER_API_KEY.",
      );
    }
    this.apiKey = apiKey;
  }

  /** Generic GET against any endpoint under /beta, e.g. "/live/congresstrading". */
  async get<T = unknown>(
    path: string,
    params?: Record<string, string | number | boolean | undefined>,
  ): Promise<T> {
    const url = new URL(BASE_URL + path);
    for (const [key, value] of Object.entries(params ?? {})) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        Accept: "application/json",
      },
    });

    if (!res.ok) {
      throw new QuiverApiError(res.status, path, await res.text());
    }
    return (await res.json()) as T;
  }

  /** Most recent trades for a dataset across all tickers, e.g. "congresstrading". */
  live<T = unknown>(dataset: string, params?: Record<string, string | number>): Promise<T> {
    return this.get<T>(`/live/${dataset}`, params);
  }

  /** Full history for a dataset, optionally scoped to one ticker. */
  historical<T = unknown>(dataset: string, ticker?: string): Promise<T> {
    return this.get<T>(ticker ? `/historical/${dataset}/${ticker}` : `/historical/${dataset}`);
  }

  // --- Convenience wrappers for the most-used datasets ---

  /** Congressional (Senate & House) stock trading disclosures. */
  getCongressTrading(ticker?: string): Promise<unknown> {
    return ticker ? this.historical("congresstrading", ticker) : this.live("congresstrading");
  }

  /** Corporate insider (Form 4) transactions. */
  getInsiderTrading(ticker?: string): Promise<unknown> {
    return ticker ? this.historical("insiders", ticker) : this.live("insiders");
  }

  /** Corporate lobbying disclosures. */
  getLobbying(ticker?: string): Promise<unknown> {
    return ticker ? this.historical("lobbying", ticker) : this.live("lobbying");
  }
}

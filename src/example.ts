import { QuiverClient } from "./quiverClient.js";

const client = new QuiverClient();

const [congress, insiders, lobbying] = await Promise.all([
  client.getCongressTrading("AAPL"),
  client.getInsiderTrading("AAPL"),
  client.getLobbying("AAPL"),
]);

console.log("Congress trading:", congress);
console.log("Insider trading:", insiders);
console.log("Lobbying:", lobbying);

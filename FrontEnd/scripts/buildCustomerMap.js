import fs from "fs";
import path from "path";

const root = process.cwd().includes("FrontEnd")
  ? process.cwd()
  : path.resolve("FrontEnd");
const inputPath = path.resolve(root, "ClickStream.csv");
const outputPath = path.resolve(root, "src/data/customerMap.js");

const adjectives = [
  "citrus",
  "amber",
  "sunny",
  "fresh",
  "mellow",
  "zesty",
  "crisp",
  "breezy",
  "velvet",
  "brisk"
];

const nouns = [
  "otter",
  "sparrow",
  "baker",
  "sprout",
  "harvest",
  "grove",
  "market",
  "orchard",
  "ridge",
  "meadow"
];

const randomNamePool = [];
for (let i = 0; i < adjectives.length; i += 1) {
  for (let j = 0; j < nouns.length; j += 1) {
    randomNamePool.push(`${adjectives[i]}-${nouns[j]}-${String(j + 1).padStart(2, "0")}`);
  }
}

const csv = fs.readFileSync(inputPath, "utf8").trim().split(/\r?\n/);
const rows = csv.slice(1);
const ids = Array.from(
  new Set(
    rows
      .map((line) => line.split(",")[0])
      .filter((id) => id && id !== "customer_id")
  )
).sort((a, b) => Number(a) - Number(b));

if (ids.length > randomNamePool.length) {
  throw new Error("Not enough generated usernames for all customer ids");
}

const customers = ids.map((id, idx) => ({
  id: `C${String(idx + 1).padStart(3, "0")}`,
  username: randomNamePool[idx]
}));

const file = `// Auto-generated from ClickStream.csv. Do not edit manually.
export const customers = ${JSON.stringify(customers, null, 2)};
export const usernameToCustomerId = Object.fromEntries(customers.map(c => [c.username, c.id]));
export const customerIdToUsername = Object.fromEntries(customers.map(c => [c.id, c.username]));
`;

fs.writeFileSync(outputPath, file, "utf8");
console.log(`Wrote ${customers.length} customer mappings to ${outputPath}`);

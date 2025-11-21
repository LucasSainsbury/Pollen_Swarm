import fs from "fs";
import path from "path";

// Simple helper to pick a random item from an array
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

// Curated image pools per category (Unsplash static URLs)
const categoryImages = {
  produce: [
    "https://images.unsplash.com/photo-1506808547685-e2ba962ded58?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1506806732259-39c2d0268443?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1505253216365-4b3356b15cfc?auto=format&fit=crop&w=600&q=80"
  ],
  meat: [
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1604908177035-0ac1c9bb646f?auto=format&fit=crop&w=600&q=80"
  ],
  pork: [
    "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1604908177035-0ac1c9bb646f?auto=format&fit=crop&w=600&q=80"
  ],
  snacks: [
    "https://images.unsplash.com/photo-1514996937319-344454492b37?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
  ],
  chocolate: [
    "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
  ],
  beverages: [
    "https://images.unsplash.com/photo-1544145945-f90425340c7b?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1510626176961-4b37d0b4e904?auto=format&fit=crop&w=600&q=80"
  ],
  tea: [
    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
  ],
  bakery: [
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
  ],
  dairy: [
    "https://images.unsplash.com/photo-1541599540903-216a46ca1dc0?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
  ]
};

// Keyword-based overrides for product names
const keywordImages = {
  potato:
    "https://images.unsplash.com/photo-1506806732259-39c2d0268443?auto=format&fit=crop&w=600&q=80",
  pork:
    "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80",
  chocolate:
    "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80",
  tea: "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=600&q=80",
  apple:
    "https://images.unsplash.com/photo-1510626176961-4b37d0b4e904?auto=format&fit=crop&w=600&q=80",
  bread:
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
  cheese:
    "https://images.unsplash.com/photo-1541599540903-216a46ca1dc0?auto=format&fit=crop&w=600&q=80",
  salmon:
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
};

const fallbackImages = [
  "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80",
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"
];

const csvPath = path.resolve("DIM_item_202511201338.csv");
const outputPath = path.resolve("DIM_item_202511201338_with_images.csv");

const splitCsvLine = (line) =>
  line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/).map((cell) => cell.replace(/^"(.*)"$/, "$1"));

const readCsv = (filePath) => {
  const raw = fs.readFileSync(filePath, "utf8").trim();
  const [headerLine, ...rows] = raw.split(/\r?\n/);
  return { headerLine, rows };
};

const formatCell = (value) => {
  if (value === undefined || value === null) return "";
  const needsQuotes = /[,"]/.test(value);
  const safe = value.replace(/"/g, '""');
  return needsQuotes ? `"${safe}"` : safe;
};

const chooseImage = (name, category, subCategory) => {
  const nameKey = (name || "").toLowerCase();
  const keywordMatch = Object.keys(keywordImages).find((key) =>
    nameKey.includes(key)
  );
  if (keywordMatch) return keywordImages[keywordMatch];

  const catKey = (category || "").toLowerCase();
  const subKey = (subCategory || "").toLowerCase();
  if (categoryImages[subKey]) return pick(categoryImages[subKey]);
  if (categoryImages[catKey]) return pick(categoryImages[catKey]);
  return pick(fallbackImages);
};

const { headerLine, rows } = readCsv(csvPath);

const updatedRows = rows.map((line) => {
  if (!line.trim()) return null;
  const cells = splitCsvLine(line);
  // columns: sku_id, product_name, description, brand, category, sub_category, price, image_url, stock_quantity
  const imageUrlIdx = 7;
  if (!cells[imageUrlIdx] || cells[imageUrlIdx] === '""') {
    const name = cells[1];
    const category = cells[4];
    const subCategory = cells[5];
    cells[imageUrlIdx] = chooseImage(name, category, subCategory);
  }
  return cells.map(formatCell).join(",");
});

const output = [headerLine, ...updatedRows.filter(Boolean)].join("\n");
fs.writeFileSync(outputPath, `${output}\n`, "utf8");

console.log(`Wrote file with images to ${outputPath}`);

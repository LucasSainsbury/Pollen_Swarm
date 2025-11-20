import fs from "fs";
import path from "path";

const withImages = path.resolve("DIM_item_202511201338_with_images.csv");
const baseFile = path.resolve("DIM_item_202511201338.csv");
const sourcePath = fs.existsSync(withImages) ? withImages : baseFile;
const outputPath = path.resolve("src/data/products.js");

const splitCsvLine = (line) =>
  line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/).map((cell) => cell.replace(/^"(.*)"$/, "$1"));

const slugify = (text) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

const csvRaw = fs.readFileSync(sourcePath, "utf8").trim();
const [headerLine, ...rows] = csvRaw.split(/\r?\n/);
const headers = splitCsvLine(headerLine);

const products = rows
  .filter((line) => line.trim())
  .map((line) => {
    const cells = splitCsvLine(line);
    const record = Object.fromEntries(headers.map((h, idx) => [h, cells[idx] ?? ""]));
    const sku = record.sku_id || record.id || slugify(record.product_name);
    return {
      id: String(sku),
      name: record.product_name,
      description: record.description,
      brand: record.brand,
      category: record.category,
      subCategory: record.sub_category,
      price: Number.parseFloat(record.price) || 0,
      image: record.image_url || "",
      stock: Number.parseInt(record.stock_quantity || "0", 10)
    };
  });

const fileContent =
  `// Auto-generated from ${path.basename(sourcePath)}. Do not edit manually.\n` +
  `export const products = ${JSON.stringify(products, null, 2)};\n`;

fs.writeFileSync(outputPath, fileContent, "utf8");

console.log(`Wrote ${products.length} products to ${outputPath}`);

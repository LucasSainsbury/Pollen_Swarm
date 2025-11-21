import { products } from "../data/products";
import { usernameToCustomerId, customerIdToUsername } from "../data/customerMap";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
// Base for recommendation API (mounted at /reco in the backend)
const RECO_API_BASE = "http://localhost:8000";
const RECO_PRODUCTS_PATH =
  import.meta.env.VITE_RECO_PRODUCTS_PATH ||
  "data/products.csv";
const RECO_TRANSACTIONS_PATH =
  import.meta.env.VITE_RECO_TRANSACTIONS_PATH ||
  "data/transactions.csv";
const RECO_CLICKSTREAM_PATH =
  import.meta.env.VITE_RECO_CLICKSTREAM_PATH ||
  "data/clickstream.csv";
const IMAGE_API_BASE = "http://localhost:9000";

export async function fetchUserProfile(identifier) {
  await delay(250);
  const username = identifier || "guest";
  const customerId = usernameToCustomerId[username];

  if (!customerId) {
    throw new Error("User not found");
  }

  return {
    email: `${username}@example.com`,
    name: username,
    customerId,
    username: customerIdToUsername[customerId] || username,
    previousInteractions: [
      { type: "view", productId: "sourdough", timestamp: Date.now() - 86400000 },
      { type: "search", query: "berries", timestamp: Date.now() - 43200000 }
    ]
  };
}

export async function trackInteraction(event) {
  await delay(120);
  console.info("Sent interaction to API", event);
  return { ok: true };
}

export async function fetchProducts(query = "") {
  await delay(120);
  if (!query) return products;
  const term = query.toLowerCase();
  return products.filter(
    (item) =>
      item.name.toLowerCase().includes(term) ||
      item.category.toLowerCase().includes(term)
  );
}

export async function fetchProductById(id) {
  await delay(120);
  return products.find((p) => p.id === id);
}

export async function fetchRecommendation({
  customerId,
  productsPath = RECO_PRODUCTS_PATH,
  transactionsPath = RECO_TRANSACTIONS_PATH,
  clickstreamPath = RECO_CLICKSTREAM_PATH
}) {
  const resp = await fetch(`${RECO_API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customer_id: customerId,
      products_path: productsPath,
      transactions_path: transactionsPath,
      clickstream_path: clickstreamPath
    })
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(
      `Recommendation API failed (${resp.status}): ${detail || resp.statusText}`
    );
  }

  return resp.json();
}

export async function fetchGeneratedImage({
  productName,
  productCategory,
  theme = "christmas_festive",
  layout = "square"
}) {
  const resp = await fetch(`${IMAGE_API_BASE}/generate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      product_name: productName,
      product_category: productCategory,
      theme,
      layout,
      as_base64: true
    })
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(
      `Image generation failed (${resp.status}): ${detail || resp.statusText}`
    );
  }

  const contentType = resp.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const data = await resp.json();
    if (!data.image_base64) {
      throw new Error("No image returned from generator");
    }
    return `data:image/png;base64,${data.image_base64}`;
  }

  // Fall back to binary response (older API)
  const blob = await resp.blob();
  return URL.createObjectURL(blob);
}

export async function fetchRandomCreative() {
  await delay(180);
  const headlines = [
    "Sunrise fruits just landed",
    "Midweek deli picks",
    "Cupboard heroes under £3",
    "Fresh bakery favourites",
    "Ready in 20: quick dinners"
  ];
  const bodies = [
    "Stock up before they go. Hand-picked for busy weeks.",
    "Pair with your usuals and keep the basket light.",
    "Fast swaps for your last shop — refreshed for you.",
    "Warm, hearty, and delivered in a click.",
    "Stretch your basket with flavour, not fuss."
  ];
  const colors = ["#f97316", "#ea580c", "#f59e0b", "#fb923c", "#f97316"];
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  return {
    title: pick(headlines),
    body: pick(bodies),
    cta: "Browse picks",
    color: pick(colors)
  };
}

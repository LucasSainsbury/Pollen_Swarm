import { products } from "../data/products";
import { usernameToCustomerId, customerIdToUsername } from "../data/customerMap";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

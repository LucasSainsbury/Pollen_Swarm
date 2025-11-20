# Pollen Swarm
Hackathon Repo for Team Auto coder

![White Board](https://github.com/user-attachments/assets/6f20f368-36ee-48e2-aa6a-7e0d58a7b8c0)

## Quick start

```bash
npm install
npm run dev
```

## What was added

- Vite + React front-end with routes for login, product list, and product detail.
- Interaction tracking context that logs searches, product views, and add-to-basket clicks, then posts them to an API stub (`src/context/InteractionContext.jsx`, `src/services/api.js`).
- Dynamic ad panel that refreshes creative based on the latest interaction (`src/hooks/useAdEngine.js`, `src/components/AdPanel.jsx`).
- Mock product catalogue and search with instant filtering (`src/data/products.js`, `src/pages/ProductListPage.jsx`).
- Minimal styling and favicon to visualize the flows (`src/styles.css`).
- When not signed in, the ad panel pulls a random creative from a mock API and swaps once interactions begin (`src/services/api.js`, `src/components/AdPanel.jsx`).
- Utility script to enrich the provided CSV with category/name-based image URLs (`scripts/fillImages.js` → writes `DIM_item_202511201338_with_images.csv`).
- Basket and checkout flow: add/update items, basket totals, and a simple checkout form with confirmation (`src/context/BasketContext.jsx`, `src/pages/BasketPage.jsx`, `src/pages/CheckoutPage.jsx`).

## Structure

- `src/pages/HomePage.jsx` – landing with random product picks and CTA to login.
- `src/pages/LoginPage.jsx` – Sainsbury's-inspired login (username/password) sending username to BE and fetching previous interactions.
- `src/pages/ProductListPage.jsx` – search bar, product cards, ads, interaction feed.
- `src/pages/ProductDetailPage.jsx` – product detail with interaction tracking for views/add-to-basket.

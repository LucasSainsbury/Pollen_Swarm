# Pollen Swarm
Hackathon Repo for Team Auto coder

![White Board](https://github.com/user-attachments/assets/6f20f368-36ee-48e2-aa6a-7e0d58a7b8c0)

## Project Structure
- `FrontEnd/` – React app (Vite) with login, products, basket/checkout, interaction tracking, and recommendation fetch.
- `personalisation_algo/` – Python recommendation engine with FastAPI wrapper.

## Prerequisites
- Node.js (18+ recommended) and npm.
- Python 3.10+.

## Setup: Frontend (React)
1) `cd FrontEnd`
2) Install deps: `npm install`
3) (Optional) Configure API paths via `.env` (Vite):
   ```
   VITE_RECO_PRODUCTS_PATH=personalisation_algo/data/products.csv
   VITE_RECO_TRANSACTIONS_PATH=personalisation_algo/data/transactions.csv
   VITE_RECO_CLICKSTREAM_PATH=personalisation_algo/data/clickstream.csv
   ```
   Defaults point to `data/*.csv`.
4) Start dev server: `npm run dev`
5) Open the shown localhost URL.

## Setup: Recommendation API (FastAPI)
1) `cd personalisation_algo`
2) Create venv and install deps:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn pydantic pandas pyyaml
   ```
   (Add any other engine deps you need here.)
3) Run the API:
   ```
   python -m src.main
   ```
   It serves at `http://0.0.0.0:8000/recommend`.

### Recommend endpoint
`POST /recommend`
Body:
```json
{
  "customer_id": "C001",
  "products_path": "data/products.csv",
  "transactions_path": "data/transactions.csv",
  "clickstream_path": "data/clickstream.csv"
}
```
Returns a recommendation payload or 404 if none.

## Frontend → API flow
- On product view, if the user is logged in (customerId available), the frontend calls `POST /recommend` with the JSON above and surfaces the suggested item in the sidebar.
- Interaction events (view, add_to_cart, purchase) are tracked client-side with placeholders for backend wiring.

## Customer IDs & Login
- Customer IDs come from `FrontEnd/src/data/customerMap.js` (generated from `ClickStream.csv` via `FrontEnd/scripts/buildCustomerMap.js`).
- IDs are formatted `C001`, `C002`, etc.; username `kazeem` maps to `C001` for quick testing.
- Unknown usernames throw “User not found” on login.

## Basket & Checkout
- Add products to basket from list/detail. Basket counts show in nav when signed in.
- Checkout posts a purchase interaction and clears the basket.

## Scripts
- `FrontEnd/scripts/buildCustomerMap.js`: generate `src/data/customerMap.js` from `FrontEnd/ClickStream.csv` with friendly usernames. Run: `node scripts/buildCustomerMap.js` (from `FrontEnd/`).
- `FrontEnd/scripts/csvToProducts.js`: regenerate `src/data/products.js` from the CSV catalogue. Run: `node scripts/csvToProducts.js`.

## Notes
- Git commits may be blocked in this environment; run `git add/commit` locally if needed.
- Ensure file paths in the API payload match where your CSVs live; defaults assume `personalisation_algo/data`.

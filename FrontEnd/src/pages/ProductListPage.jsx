import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchProducts } from "../services/api";
import SearchBar from "../components/SearchBar";
import ProductCard from "../components/ProductCard";
import AdPanel from "../components/AdPanel";
import InteractionFeed from "../components/InteractionFeed";
import { useInteraction } from "../context/InteractionContext";
import { useBasket } from "../context/BasketContext";

export default function ProductListPage() {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const { trackInteraction, user } = useInteraction();
  const { addToBasket } = useBasket();
  const lastAutoSearch = useRef("");
  const navigate = useNavigate();

  const loadProducts = async (searchTerm = "") => {
    setLoading(true);
    const results = await fetchProducts(searchTerm);
    setItems(results);
    setLoading(false);
    setPage(1);
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleQueryChange = (value) => {
    setQuery(value);
    if (!value.trim()) {
      loadProducts();
      lastAutoSearch.current = "";
    }
  };

  const handleSearch = async () => {
    const term = query.trim();
    await loadProducts(term);
    if (term) {
      trackInteraction({ type: "search", query: term });
      lastAutoSearch.current = term;
    }
  };

  useEffect(() => {
    const term = query.trim();
    if (term.length < 3 || term === lastAutoSearch.current) {
      return undefined;
    }
    const timer = setTimeout(async () => {
      await loadProducts(term);
      trackInteraction({ type: "search", query: term });
      lastAutoSearch.current = term;
    }, 250);
    return () => clearTimeout(timer);
  }, [query, trackInteraction]);

  const handleProductClick = (product) => {
    trackInteraction({
      type: "view",
      eventType: "view",
      productId: product.id,
      source: "product_list"
    });
  };

  const handleAdd = (product) => {
    if (!user) {
      navigate("/login", { state: { from: `/products/${product.id}` } });
      return;
    }
    addToBasket(product, 1);
    trackInteraction({
      type: "add_to_basket",
      eventType: "add_to_cart",
      productId: product.id,
      source: "product_list"
    });
  };

  const pageSize = 12;
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const pagedItems = items.slice((page - 1) * pageSize, page * pageSize);

  const nextPage = () => setPage((p) => Math.min(totalPages, p + 1));
  const prevPage = () => setPage((p) => Math.max(1, p - 1));

  console.log("pafedIrem", pagedItems)

  return (
    <div className="grid">
      <section className="stack">
        <div className="card">
          <div className="card-head">
            <div>
              <div className="eyebrow">Browse groceries</div>
              <h2>Find products quickly</h2>
            </div>
            <SearchBar
              value={query}
              onChange={handleQueryChange}
              onSubmit={handleSearch}
              placeholder="Search by name or category"
            />
          </div>
          {loading ? (
            <div className="muted">Loading...</div>
          ) : (
            <div className="product-grid">
              {pagedItems.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onClick={() => handleProductClick(product)}
                  onAdd={handleAdd}
                />
              ))}
              {!items.length && <p>No products match that search.</p>}
            </div>
          )}
          {!!items.length && (
            <div className="pagination">
              <button
                className="ghost-btn"
                onClick={prevPage}
                disabled={page === 1}
              >
                ← Previous
              </button>
              <div className="muted">
                Page {page} of {totalPages}
              </div>
              <button
                className="ghost-btn"
                onClick={nextPage}
                disabled={page === totalPages}
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </section>
      <aside className="stack">
        <AdPanel />
        <InteractionFeed />
      </aside>
    </div>
  );
}

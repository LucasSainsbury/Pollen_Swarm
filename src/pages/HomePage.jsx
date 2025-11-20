import React, { useMemo } from "react";
import { Link } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import AdPanel from "../components/AdPanel";
import { useInteraction } from "../context/InteractionContext";
import { products } from "../data/products";

const sampleProducts = (items, count) => {
  const shuffled = [...items].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

export default function HomePage() {
  const { trackInteraction, user } = useInteraction();
  const picks = useMemo(() => sampleProducts(products, 6), []);

  const onProductClick = (product) =>
    trackInteraction({ type: "hero_view", productId: product.id });

  return (
    <div className="grid">
      <section className="stack">
        <div className="card">
          <div className="card-head">
            <div>
              <div className="eyebrow">Fresh for you</div>
              <h2>Today&apos;s picks</h2>
              <p className="muted">
                A rotating mix of favourites and seasonal finds. Click any item
                to view more.
              </p>
            </div>
          </div>
          <div className="product-grid">
            {picks.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onClick={() => onProductClick(product)}
              />
            ))}
          </div>
        </div>
      </section>
      <aside className="stack">
        <AdPanel />
        {!user && (
          <div className="promo-card">
            <div className="eyebrow">Personalised offers</div>
            <h3>Shop with tailored picks</h3>
            <p className="muted">
              Sign in to pull your past browsing and basket picks so offers and
              recommendations stay fresh while you shop.
            </p>
            <Link className="solid-btn wide" to="/login">
              Sign in to shop smarter
            </Link>
          </div>
        )}
      </aside>
    </div>
  );
}

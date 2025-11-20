import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { fetchProductById } from "../services/api";
import { useInteraction } from "../context/InteractionContext";
import AdPanel from "../components/AdPanel";
import InteractionFeed from "../components/InteractionFeed";
import { useBasket } from "../context/BasketContext";

export default function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const { trackInteraction, user } = useInteraction();
  const { addToBasket } = useBasket();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const result = await fetchProductById(id);
      setProduct(result);
      setLoading(false);
      trackInteraction({
        type: "view",
        eventType: "view",
        productId: id,
        source: "product_detail"
      });
    };
    load();
  }, [id, trackInteraction]);

  if (loading) return <p className="muted">Loading product...</p>;
  if (!product) return <p>Not found</p>;

  const handleAdd = () => {
    if (!user) {
      navigate("/login", { state: { from: location.pathname } });
      return;
    }
    addToBasket(product, 1);
    trackInteraction({
      type: "add_to_basket",
      eventType: "add_to_cart",
      productId: id,
      source: "product_detail"
    });
  };

  return (
    <div className="grid">
      <section className="card detail">
        <Link to="/products" className="ghost-btn">
          ← Back to products
        </Link>
        <div className="detail-body">
          <img src={product.image} alt={product.name} />
          <div className="detail-copy">
            <div className="eyebrow">{product.category}</div>
            <h1>{product.name}</h1>
            <p className="muted">{product.description}</p>
            <div className="price-lg">£{product.price.toFixed(2)}</div>
            <div className="detail-actions">
              <button className="solid-btn" onClick={handleAdd}>
                Add to basket
              </button>
            </div>
          </div>
        </div>
      </section>
      <aside className="stack">
        <AdPanel />
        <InteractionFeed />
      </aside>
    </div>
  );
}

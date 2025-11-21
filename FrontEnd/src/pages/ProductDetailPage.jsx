import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import {
  fetchProductById,
  fetchRecommendation,
  fetchGeneratedImage
} from "../services/api";
import { useInteraction } from "../context/InteractionContext";
import AdPanel from "../components/AdPanel";
import { useBasket } from "../context/BasketContext";

export default function ProductDetailPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reco, setReco] = useState(null);
  const [recoError, setRecoError] = useState("");
  const [recoLoading, setRecoLoading] = useState(false);
  const [creativeSrc, setCreativeSrc] = useState("");
  const [creativeError, setCreativeError] = useState("");
  const [creativeLoading, setCreativeLoading] = useState(false);
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

  useEffect(() => {
    const runReco = async () => {
      if (!user?.customerId) return;
      setRecoLoading(true);
      setRecoError("");
      try {
        const rec = await fetchRecommendation({ customerId: user.customerId });
        setReco(rec);
      } catch (err) {
        setRecoError(err.message);
      } finally {
        setRecoLoading(false);
      }
    };
    runReco();
  }, [user, id]);

  useEffect(() => {
    const runCreative = async () => {
      if (!reco || !reco.product_name) return;
      setCreativeLoading(true);
      setCreativeError("");
      try {
        const img = await fetchGeneratedImage({
          productName: reco.product_name,
          productCategory: reco.product_category || product?.category || ""
        });
        setCreativeSrc(img);
      } catch (err) {
        setCreativeError(err.message);
      } finally {
        setCreativeLoading(false);
      }
    };
    runCreative();
  }, [reco, product]);

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
      </aside>
    </div>
  );
}

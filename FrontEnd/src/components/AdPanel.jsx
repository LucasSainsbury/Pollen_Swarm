import React, { useEffect, useState } from "react";
import { useAdEngine } from "../hooks/useAdEngine";
import { useInteraction } from "../context/InteractionContext";
import { fetchRandomCreative } from "../services/api";

export default function AdPanel() {
  const { lastInteraction, user } = useInteraction();
  const [anonCreative, setAnonCreative] = useState(null);
  const creative = useAdEngine(lastInteraction);

  useEffect(() => {
    if (!user && !lastInteraction) {
      fetchRandomCreative().then(setAnonCreative).catch(() => {});
    }
  }, [user, lastInteraction]);

  const displayCreative =
    !user && !lastInteraction && anonCreative ? anonCreative : creative;

  return (
    <div className="ad-panel" style={{ background: displayCreative.color }}>
      <div className="ad-content">
        <div className="eyebrow">Dynamic creative</div>
        <h3>{displayCreative.title}</h3>
        <p>{displayCreative.body}</p>
        <button className="solid-btn">{displayCreative.cta}</button>
      </div>
      {displayCreative.product && (
        <div className="ad-product">
          <img
            src={displayCreative.product.image}
            alt={displayCreative.product.name}
          />
          <div className="ad-meta">
            <div className="ad-name">{displayCreative.product.name}</div>
            <div className="ad-price">
              £{displayCreative.product.price.toFixed(2)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

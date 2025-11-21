import React, { useEffect, useState } from "react";
import { useAdEngine } from "../hooks/useAdEngine";
import { useInteraction } from "../context/InteractionContext";
import { fetchRandomCreative } from "../services/api";
import GamificationGame from "./GamificationGame";

export default function AdPanel() {
  const { lastInteraction, user } = useInteraction();
  const [anonCreative, setAnonCreative] = useState(null);
  const creative = useAdEngine(lastInteraction);
  const [showGame, setShowGame] = useState(false);

  useEffect(() => {
    if (!user && !lastInteraction) {
      fetchRandomCreative().then(setAnonCreative).catch(() => {});
    }
  }, [user, lastInteraction]);

  const displayCreative =
    !user && !lastInteraction && anonCreative ? anonCreative : creative;

  return (
    <div
      className="ad-panel"
      style={{
        background: "#fff",
        position: "relative",
        overflow: "hidden",
        borderRadius: 24,
        padding: 0,
        minHeight: 'unset', // Remove forced full height
        height: 'auto', // Let content determine height
        display: "flex",
        flexDirection: "column",
        width: 380,
        maxWidth: "100%",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          aspectRatio: '0.7', // Make ad image area even taller (portrait)
          borderTopLeftRadius: 24,
          borderTopRightRadius: 24,
          overflow: "hidden",
          background: `url('/ad.avif') center/cover no-repeat`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {!showGame && (
          <button
            className="solid-btn"
            style={{
              fontSize: "1.3rem",
              padding: "16px 28px",
              borderRadius: 22,
              background: "linear-gradient(90deg,#7b2ff2,#f357a8)",
              color: "#fff",
              fontWeight: 700,
              boxShadow: "0 4px 24px #7b2ff288",
              border: "none",
              cursor: "pointer",
              opacity: 0.97,
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              zIndex: 2,
            }}
            onClick={() => setShowGame(true)}
          >
            Click Here to Win the Prize
          </button>
        )}
        {showGame && (
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0, // Ensure overlay starts at top
              width: "100%",
              height: "100%",
              zIndex: 3,
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "center",
              background: "rgba(255,255,255,0.01)",
            }}
          >
            <GamificationGame onClose={() => setShowGame(false)} align="bottom" />
          </div>
        )}
      </div>
      <div
        className="ad-content"
        style={{
          position: "relative",
          zIndex: 2,
          padding: 24,
          background: displayCreative.color,
          borderBottomLeftRadius: 24,
          borderBottomRightRadius: 24,
          marginBottom: 0, // Remove extra margin
        }}
      >
        <h3>{displayCreative.title}</h3>
        <p>{displayCreative.body}</p>
        <button className="solid-btn">{displayCreative.cta}</button>
      </div>
      {displayCreative.product && (
        <div className="ad-product" style={{ position: "relative", zIndex: 4 }}>
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

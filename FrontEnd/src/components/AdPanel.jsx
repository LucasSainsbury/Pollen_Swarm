import React, { useEffect, useState } from "react";
import { useAdEngine } from "../hooks/useAdEngine";
import { useInteraction } from "../context/InteractionContext";
import { fetchRandomCreative, fetchGeneratedImage } from "../services/api";

export default function AdPanel() {
  const { lastInteraction, user } = useInteraction();
  const [anonCreative, setAnonCreative] = useState(null);
  const [creativeImg, setCreativeImg] = useState("");
  const [imgError, setImgError] = useState("");
  const [imgLoading, setImgLoading] = useState(false);
  const creative = useAdEngine(lastInteraction);

  useEffect(() => {
    if (!user) {
      setAnonCreative(null);
      return;
    }
    if (!lastInteraction) {
      fetchRandomCreative().then(setAnonCreative).catch(() => {});
    }
  }, [user, lastInteraction]);

  if (!user) return null;

  const displayCreative =
    !lastInteraction && anonCreative ? anonCreative : creative;

  useEffect(() => {
    const loadImage = async () => {
      if (!displayCreative?.product) {
        setCreativeImg("");
        return;
      }
      setImgLoading(true);
      setImgError("");
      try {
        const img = await fetchGeneratedImage({
          productName: displayCreative.product.name,
          productCategory: displayCreative.product.category
        });
        setCreativeImg(img);
      } catch (err) {
        setImgError(err.message);
        setCreativeImg("");
      } finally {
        setImgLoading(false);
      }
    };
    loadImage();
  }, [displayCreative]);

  return (
    <div
      className="ad-panel"
      style={{
        background: displayCreative?.color || "#111827",
        position: "relative",
        overflow: "hidden"
      }}
    >
      {creativeImg ? (
        <img
          src={creativeImg}
          alt={displayCreative?.product?.name || "Creative"}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover"
          }}
        />
      ) : (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#e5e7eb",
            fontWeight: 600,
            letterSpacing: "0.08em"
          }}
        >
          {imgLoading ? "⏳ Loading creative" : "Preparing creative"}
        </div>
      )}
      {imgError && (
        <div className="ad-content">
          <p className="muted">Creative error: {imgError}</p>
        </div>
      )}
    </div>
  );
}

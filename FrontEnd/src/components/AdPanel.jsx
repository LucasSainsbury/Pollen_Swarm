import React, { useEffect, useState } from "react";
import { useAdEngine } from "../hooks/useAdEngine";
import { useInteraction } from "../context/InteractionContext";
import {
  fetchRandomCreative,
  fetchGeneratedImage,
  fetchRecommendation
} from "../services/api";

export default function AdPanel() {
  const { lastInteraction, user } = useInteraction();
  const [anonCreative, setAnonCreative] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recoError, setRecoError] = useState("");
  const [creativeImg, setCreativeImg] = useState("");
  const [imgError, setImgError] = useState("");
  const [imgLoading, setImgLoading] = useState(false);
  const creative = useAdEngine(lastInteraction);

  useEffect(() => {
    if (!user) {
      setAnonCreative(null);
      setRecommendation(null);
      setRecoError("");
      return;
    }
    if (!lastInteraction) {
      fetchRandomCreative().then(setAnonCreative).catch(() => {});
    }
  }, [user, lastInteraction]);

  useEffect(() => {
    const runRecommendation = async () => {
      if (!user?.customerId) return;
      setRecoError("");
      try {
        const rec = await fetchRecommendation({ customerId: user.customerId });
        setRecommendation(rec);
      } catch (err) {
        setRecommendation(null);
        setRecoError(err.message);
      }
    };
    runRecommendation();
  }, [user, lastInteraction]);

  if (!user) return null;

  const recoCreative = recommendation
    ? {
        title: "Your recommended pick",
        body: `We think you'll like ${recommendation.product_name}. Pair it with top ${
          recommendation.product_category || "picks"
        } today.`,
        cta: "See details",
        color: "#2563eb",
        product: {
          name: recommendation.product_name,
          category: recommendation.product_category
        }
      }
    : null;

  const displayCreative =
    recoCreative || (!lastInteraction && anonCreative ? anonCreative : creative);

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

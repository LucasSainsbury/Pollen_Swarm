import React from "react";
import { useInteraction } from "../context/InteractionContext";

const label = (item) => {
  if (item.productId) return `Viewed ${item.productId}`;
  if (item.query) return `Searched "${item.query}"`;
  return item.type || "Interaction";
};

export default function InteractionFeed() {
  const { interactions } = useInteraction();
  if (!interactions.length) return null;

  return (
    <div className="interaction-feed">
      <div className="eyebrow">Latest interactions</div>
      <ul>
        {interactions.slice(0, 6).map((item, idx) => (
          <li key={idx}>
            <span>{label(item)}</span>
            <span className="time">
              {new Date(item.timestamp).toLocaleTimeString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

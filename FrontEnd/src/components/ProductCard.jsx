import React from "react";
import { Link } from "react-router-dom";

export default function ProductCard({ product, onClick, onAdd }) {
  return (
    <article className="product-card">
      <Link to={`/products/${product.id}`} onClick={onClick}>
        <img src={product.image} alt={product.name} />
        <div className="product-body">
          <div className="eyebrow">{product.category}</div>
          <h4>{product.name}</h4>
          <div className="price">£{product.price.toFixed(2)}</div>
        </div>
      </Link>
      {onAdd && (
        <div className="product-actions">
          <button className="solid-btn" onClick={() => onAdd(product)}>
            Add to basket
          </button>
        </div>
      )}
    </article>
  );
}

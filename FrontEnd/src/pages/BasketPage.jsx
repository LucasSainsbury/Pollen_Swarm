import React from "react";
import { Link } from "react-router-dom";
import { useBasket } from "../context/BasketContext";

export default function BasketPage() {
  const { itemsArray, totalItems, totalCost, updateQuantity, clearBasket } =
    useBasket();

  const handleQuantity = (id, qty) => {
    updateQuantity(id, Math.max(0, qty));
  };

  if (!itemsArray.length) {
    return (
      <div className="card">
        <div className="eyebrow">Basket</div>
        <h2>Your basket is empty</h2>
        <p className="muted">Browse products to start filling your basket.</p>
        <Link className="solid-btn" to="/products">
          Browse products
        </Link>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <div className="eyebrow">Basket</div>
          <h2>
            {totalItems} item{totalItems !== 1 ? "s" : ""} • £
            {totalCost.toFixed(2)}
          </h2>
        </div>
        <button className="ghost-btn" onClick={clearBasket}>
          Clear basket
        </button>
      </div>
      <div className="basket-list">
        {itemsArray.map(({ product, quantity }) => (
          <div className="basket-row" key={product.id}>
            <img src={product.image} alt={product.name} />
            <div className="basket-info">
              <div className="eyebrow">{product.category}</div>
              <div className="basket-name">{product.name}</div>
              <div className="muted">£{product.price.toFixed(2)} each</div>
            </div>
            <div className="basket-qty">
              <button
                className="ghost-btn"
                onClick={() => handleQuantity(product.id, quantity - 1)}
              >
                -
              </button>
              <span>{quantity}</span>
              <button
                className="ghost-btn"
                onClick={() => handleQuantity(product.id, quantity + 1)}
              >
                +
              </button>
            </div>
            <div className="basket-line">
              £{(quantity * product.price).toFixed(2)}
            </div>
          </div>
        ))}
      </div>
      <div className="basket-footer">
        <div className="muted">
          Total • £{totalCost.toFixed(2)} ({totalItems} item
          {totalItems !== 1 ? "s" : ""})
        </div>
        <Link className="solid-btn" to="/checkout">
          Proceed to checkout
        </Link>
      </div>
    </div>
  );
}

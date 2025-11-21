import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useBasket } from "../context/BasketContext";
import { useInteraction } from "../context/InteractionContext";

const initialForm = {
  name: "",
  email: "",
  address: "",
  city: "",
  postcode: "",
  card: ""
};

export default function CheckoutPage() {
  const { itemsArray, totalCost, clearBasket } = useBasket();
  const [form, setForm] = useState(initialForm);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();
  const { trackInteraction } = useInteraction();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    trackInteraction({
      type: "purchase",
      eventType: "purchase",
      total: totalCost,
      items: itemsArray.map(({ product, quantity }) => ({
        productId: product.id,
        quantity,
        price: product.price
      }))
    });
    clearBasket();
    setTimeout(() => navigate("/products"), 1000);
  };

  if (!itemsArray.length && !submitted) {
    return (
      <div className="card">
        <div className="eyebrow">Checkout</div>
        <h2>No items to checkout</h2>
        <p className="muted">Add items to your basket to continue.</p>
        <Link className="solid-btn" to="/products">
          Browse products
        </Link>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="card">
        <div className="eyebrow">Checkout</div>
        <h2>Order placed</h2>
        <p className="muted">
          Thanks, {form.name || "shopper"}! Your order is confirmed.
        </p>
        <Link className="solid-btn" to="/products">
          Continue shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="grid">
      <div className="card">
        <div className="eyebrow">Your order</div>
        <div className="checkout-summary">
          {itemsArray.map(({ product, quantity }) => (
            <div className="checkout-row" key={product.id}>
              <div>
                <div className="basket-name">{product.name}</div>
                <div className="muted">
                  {quantity} x £{product.price.toFixed(2)}
                </div>
              </div>
              <div className="basket-line">
                £{(quantity * product.price).toFixed(2)}
              </div>
            </div>
          ))}
          <div className="checkout-total">
            <span>Total</span>
            <span>£{totalCost.toFixed(2)}</span>
          </div>
        </div>
        <Link to="/basket" className="ghost-btn">
          ← Back to basket
        </Link>
      </div>
      <form className="card checkout-form" onSubmit={handleSubmit}>
        <div className="eyebrow">Shipping & payment</div>
        <label>
          Full name
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Address
          <input
            name="address"
            value={form.address}
            onChange={handleChange}
            required
          />
        </label>
        <div className="two-col">
          <label>
            City
            <input
              name="city"
              value={form.city}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Postcode
            <input
              name="postcode"
              value={form.postcode}
              onChange={handleChange}
              required
            />
          </label>
        </div>
        <label>
          Card number
          <input
            name="card"
            value={form.card}
            onChange={handleChange}
            required
            placeholder="4242 4242 4242 4242"
          />
        </label>
        <button type="submit" className="solid-btn full">
          Place order
        </button>
      </form>
    </div>
  );
}

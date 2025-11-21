import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useInteraction } from "../context/InteractionContext";

export default function LoginPage() {
  const [username, setUsername] = useState("kazeem");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const { login, trackInteraction } = useInteraction();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(username);
      await trackInteraction({ type: "login", username });
      const redirectTo = location.state?.from || "/products";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err?.message || "Login failed");
    }
  };

  return (
    <div className="login-hero">
      <div className="login-panel">
        <div className="eyebrow">Sainsbury&apos;s inspired</div>
        <h1>Sign in to personalise</h1>
        <p className="muted">
          Enter your details and we&apos;ll pull your saved baskets and browsing
          so your offers and products stay in sync while you shop.
        </p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="solid-btn full">
            Continue
          </button>
        </form>
        {error && <p className="login-note" style={{ color: "#e11d48" }}>{error}</p>}
        <p className="login-note">
          Once in, your browsing will shape recommendations and offers in real
          time.
        </p>
      </div>
      <div className="login-aside">
        <div className="eyebrow">Live offers</div>
        <p>
          As you browse and search, we keep offers and suggestions refreshed in
          near real-time.
        </p>
      </div>
    </div>
  );
}

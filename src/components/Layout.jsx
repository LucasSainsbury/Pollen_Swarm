import React from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useInteraction } from "../context/InteractionContext";
import { useBasket } from "../context/BasketContext";

export default function Layout({ children }) {
  const { user, logout } = useInteraction();
  const { totalItems } = useBasket();
  const navigate = useNavigate();
  const location = useLocation();
  const isProductsPage = location.pathname.startsWith("/products");

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="page">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-mark">Pollen Swarm</span>
        </Link>
        <div className="topbar-right">
          <nav className="nav">
            <NavLink to="/products">Groceries</NavLink>
            {user && (
              <NavLink to="/basket" className="basket-link">
                <span className="basket-icon" aria-hidden="true">
                  🧺
                </span>
                Basket
                {totalItems > 0 && (
                  <span className="basket-count">{totalItems}</span>
                )}
              </NavLink>
            )}
          </nav>
          {user ? (
            <div className="user-chip">
              <div className="profile-pill">
                <div className="profile-avatar" aria-hidden="true">
                  <svg viewBox="0 0 24 24" role="presentation">
                    <path d="M12 12.5c2.34 0 4.25-1.96 4.25-4.37C16.25 5.72 14.37 4 12 4S7.75 5.72 7.75 8.13C7.75 10.54 9.66 12.5 12 12.5Zm0 2c-2.83 0-5.25 1.54-5.25 3.41 0 .55.45 1 .98 1h8.54c.53 0 .98-.45.98-1 0-1.87-2.42-3.41-5.25-3.41Z" />
                  </svg>
                </div>
                <div className="profile-name">{user.name}</div>
              </div>
              <button className="ghost-btn" onClick={handleLogout}>
                Log out
              </button>
            </div>
          ) : (
            isProductsPage && (
              <Link className="solid-btn login-btn" to="/login">
                Log in
              </Link>
            )
          )}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}

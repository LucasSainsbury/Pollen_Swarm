import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { InteractionProvider } from "./context/InteractionContext";
import { BasketProvider } from "./context/BasketContext";
import LoginPage from "./pages/LoginPage";
import ProductListPage from "./pages/ProductListPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import HomePage from "./pages/HomePage";
import BasketPage from "./pages/BasketPage";
import CheckoutPage from "./pages/CheckoutPage";

export default function App() {
  return (
    <InteractionProvider>
      <BasketProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/products" element={<ProductListPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/basket" element={<BasketPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </BasketProvider>
    </InteractionProvider>
  );
}

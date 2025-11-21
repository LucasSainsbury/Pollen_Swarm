import { useEffect, useState } from "react";
import { products } from "../data/products";

const palette = [
  "#0f766e",
  "#e11d48",
  "#1d4ed8",
  "#f97316",
  "#2563eb",
  "#047857"
];

const findProduct = (id) => products.find((p) => p.id === id);

const buildCreative = (interaction) => {
  if (!interaction) {
    return {
      title: "Hand-picked offers",
      body: "Browse what you love and we'll tailor fresh picks instantly.",
      cta: "Discover now",
      color: palette[0]
    };
  }

  const targetProduct = interaction.productId
    ? findProduct(interaction.productId)
    : null;

  if (targetProduct) {
    return {
      title: `Inspired by ${targetProduct.category}`,
      body: `Don't miss ${targetProduct.name}. Pair it with our newest arrivals in ${targetProduct.category.toLowerCase()}.`,
      cta: "See similar",
      product: targetProduct,
      color: palette[targetProduct.category.length % palette.length]
    };
  }

  if (interaction.query) {
    return {
      title: `More like "${interaction.query}"`,
      body: "We refreshed results and bundled quick starters for you.",
      cta: "View picks",
      color: palette[interaction.query.length % palette.length]
    };
  }

  return {
    title: "Trending right now",
    body: "Shoppers are loving these staples — grab yours while fresh.",
    cta: "Shop trending",
    color: palette[3]
  };
};

export function useAdEngine(trigger) {
  const [creative, setCreative] = useState(buildCreative(null));

  useEffect(() => {
    setCreative(buildCreative(trigger));
  }, [trigger]);

  return creative;
}

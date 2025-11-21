import React, { createContext, useContext, useMemo, useReducer } from "react";

const BasketContext = createContext(null);

const initialState = {
  items: {}
};

function reducer(state, action) {
  switch (action.type) {
    case "add": {
      const { product, quantity = 1 } = action;
      const existing = state.items[product.id] || { product, quantity: 0 };
      const nextQty = existing.quantity + quantity;
      return {
        ...state,
        items: {
          ...state.items,
          [product.id]: { product, quantity: nextQty }
        }
      };
    }
    case "update": {
      const { productId, quantity } = action;
      if (quantity <= 0) {
        const clone = { ...state.items };
        delete clone[productId];
        return { ...state, items: clone };
      }
      const current = state.items[productId];
      if (!current) return state;
      return {
        ...state,
        items: {
          ...state.items,
          [productId]: { ...current, quantity }
        }
      };
    }
    case "clear":
      return initialState;
    default:
      return state;
  }
}

export function BasketProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const addToBasket = (product, quantity = 1) =>
    dispatch({ type: "add", product, quantity });

  const updateQuantity = (productId, quantity) =>
    dispatch({ type: "update", productId, quantity });

  const clearBasket = () => dispatch({ type: "clear" });

  const itemsArray = Object.values(state.items);
  const totalItems = itemsArray.reduce((sum, item) => sum + item.quantity, 0);
  const totalCost = itemsArray.reduce(
    (sum, item) => sum + item.quantity * (item.product.price || 0),
    0
  );

  const value = useMemo(
    () => ({
      items: state.items,
      itemsArray,
      totalItems,
      totalCost,
      addToBasket,
      updateQuantity,
      clearBasket
    }),
    [state.items, totalItems, totalCost]
  );

  return (
    <BasketContext.Provider value={value}>{children}</BasketContext.Provider>
  );
}

export const useBasket = () => {
  const ctx = useContext(BasketContext);
  if (!ctx) throw new Error("useBasket must be used in BasketProvider");
  return ctx;
};

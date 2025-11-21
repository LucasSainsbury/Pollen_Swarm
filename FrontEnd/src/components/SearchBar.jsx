import React from "react";

export default function SearchBar({ value, onChange, onSubmit, placeholder }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.();
  };

  return (
    <form className="search" onSubmit={handleSubmit}>
      <input
        type="search"
        value={value}
        placeholder={placeholder || "Search groceries"}
        onChange={(e) => onChange(e.target.value)}
      />
      <button type="submit">Search</button>
    </form>
  );
}

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState
} from "react";
import {
  fetchUserProfile,
  trackInteraction as sendInteraction
} from "../services/api";

const InteractionContext = createContext(null);

export function InteractionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [interactions, setInteractions] = useState([]);

  const login = useCallback(async (username) => {
    const profile = await fetchUserProfile(username);
    setUser(profile);
    setInteractions(profile.previousInteractions || []);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setInteractions([]);
  }, []);

  const trackInteraction = useCallback(
    async (event) => {
      const payload = {
        ...event,
        user: user?.email ?? "anonymous",
        timestamp: Date.now()
      };

      setInteractions((prev) => [payload, ...prev].slice(0, 50));

      try {
        await sendInteraction(payload);
      } catch (err) {
        console.error("Failed to send interaction", err);
      }
    },
    [user]
  );

  const value = useMemo(
    () => ({
      user,
      interactions,
      lastInteraction: interactions[0] ?? null,
      login,
      logout,
      trackInteraction
    }),
    [user, interactions, login, logout, trackInteraction]
  );

  return (
    <InteractionContext.Provider value={value}>
      {children}
    </InteractionContext.Provider>
  );
}

export const useInteraction = () => {
  const ctx = useContext(InteractionContext);
  if (!ctx) throw new Error("useInteraction must be used in provider");
  return ctx;
};

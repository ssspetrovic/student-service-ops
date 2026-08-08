import { useEffect, useState } from "react";
import api, { clearTokens, getAccessToken, storeTokens } from "../api/client";
import AuthContext from "./context";

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    let isCurrent = true;

    const restoreSession = async () => {
      if (!getAccessToken()) {
        setIsInitializing(false);
        return;
      }

      try {
        const response = await api.get("/accounts/me/");

        if (isCurrent) {
          setUser(response.data);
        }
      } catch {
        clearTokens();
      } finally {
        if (isCurrent) {
          setIsInitializing(false);
        }
      }
    };

    restoreSession();

    return () => {
      isCurrent = false;
    };
  }, []);

  const login = async (email, password) => {
    try {
      const tokenResponse = await api.post("/auth/token/", { email, password });
      storeTokens(tokenResponse.data);

      const userResponse = await api.get("/accounts/me/");
      setUser(userResponse.data);
      return userResponse.data;
    } catch (error) {
      clearTokens();
      throw error;
    }
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isInitializing, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;

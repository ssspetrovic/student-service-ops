import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, {
  clearAccessToken,
  refreshAccessToken,
  storeAccessToken,
  subscribeToSessionExpiration,
} from "../api/client";
import AuthContext from "./context";

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    return subscribeToSessionExpiration(() => {
      setUser(null);
      setIsInitializing(false);
      navigate("/login", { replace: true });
    });
  }, [navigate]);

  useEffect(() => {
    let isCurrent = true;

    const restoreSession = async () => {
      try {
        await api.get("/auth/csrf/");
        await refreshAccessToken();
        const response = await api.get("/accounts/me/");

        if (isCurrent) {
          setUser(response.data);
        }
      } catch {
        if (isCurrent) {
          clearAccessToken();
        }
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
      storeAccessToken(tokenResponse.data.access);

      const userResponse = await api.get("/accounts/me/");
      setUser(userResponse.data);
      return userResponse.data;
    } catch (error) {
      clearAccessToken();
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.get("/auth/csrf/");
      await api.post("/auth/logout/");
    } finally {
      clearAccessToken();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isInitializing, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;

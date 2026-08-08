import axios from "axios";

const ACCESS_TOKEN_KEY = "student_service_access";
const REFRESH_TOKEN_KEY = "student_service_refresh";

const api = axios.create({
  baseURL: "/api",
});

export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);

export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

export const storeTokens = ({ access, refresh }) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
};

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

api.interceptors.request.use((config) => {
  const accessToken = getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

let refreshRequest;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config;
    const isTokenRequest =
      request?.url === "/auth/token/" ||
      request?.url === "/auth/token/refresh/";

    if (error.response?.status !== 401 || !request || isTokenRequest) {
      return Promise.reject(error);
    }

    if (request._retried) {
      clearTokens();
      return Promise.reject(error);
    }

    request._retried = true;

    try {
      refreshRequest ??= axios.post("/api/auth/token/refresh/", {
        refresh: getRefreshToken(),
      });
      const { access } = (await refreshRequest).data;

      localStorage.setItem(ACCESS_TOKEN_KEY, access);
      request.headers.Authorization = `Bearer ${access}`;
      return api(request);
    } catch (refreshError) {
      clearTokens();
      return Promise.reject(refreshError);
    } finally {
      refreshRequest = undefined;
    }
  },
);

export default api;

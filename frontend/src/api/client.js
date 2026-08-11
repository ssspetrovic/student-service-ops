import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

let accessToken = null;

export const getAccessToken = () => accessToken;

export const storeAccessToken = (access) => {
  accessToken = access;
};

export const clearAccessToken = () => {
  accessToken = null;
};

const sessionExpirationListeners = new Set();

export const subscribeToSessionExpiration = (listener) => {
  sessionExpirationListeners.add(listener);

  return () => sessionExpirationListeners.delete(listener);
};

const expireSession = () => {
  clearAccessToken();
  sessionExpirationListeners.forEach((listener) => listener());
};

let refreshRequest;

export const refreshAccessToken = async () => {
  refreshRequest ??= api
    .post("/auth/token/refresh/")
    .then(({ data }) => {
      storeAccessToken(data.access);
      return data.access;
    })
    .finally(() => {
      refreshRequest = undefined;
    });

  return refreshRequest;
};

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers ??= {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config;
    const isAuthRequest = [
      "/auth/token/",
      "/auth/token/refresh/",
      "/auth/logout/",
    ].includes(request?.url);

    if (error.response?.status !== 401 || !request || isAuthRequest) {
      return Promise.reject(error);
    }

    if (request._retried) {
      expireSession();
      return Promise.reject(error);
    }

    request._retried = true;

    try {
      const access = await refreshAccessToken();
      request.headers ??= {};
      request.headers.Authorization = `Bearer ${access}`;
      return api(request);
    } catch (refreshError) {
      expireSession();
      return Promise.reject(refreshError);
    }
  },
);

export default api;

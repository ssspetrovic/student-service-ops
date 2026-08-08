import { useState } from "react";
import api, { clearTokens, storeTokens } from "./client";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const tokenResponse = await api.post("/auth/token/", { email, password });
      storeTokens(tokenResponse.data);

      const userResponse = await api.get("/accounts/me/");
      setUser(userResponse.data);
      setPassword("");
    } catch (requestError) {
      clearTokens();
      setError(requestError.response?.data?.detail || "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = () => {
    clearTokens();
    setUser(null);
  };

  if (user) {
    return (
      <main className="container py-5">
        <div className="card shadow-sm">
          <div className="card-body p-4">
            <p className="text-primary text-uppercase fw-semibold small">
              Student Service
            </p>
            <h1 className="h2">Welcome back</h1>
            <p className="fs-5 fw-semibold mb-1">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-body-secondary">{user.email}</p>
            <p className="mb-4">Signed in as {user.role}</p>
            <button type="button" className="btn btn-outline-secondary" onClick={handleLogout}>
              Log out
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="container d-flex align-items-center min-vh-100 py-5">
      <div className="row justify-content-center w-100">
        <div className="col-sm-10 col-md-7 col-lg-5">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              <p className="text-primary text-uppercase fw-semibold small">
                Student Service
              </p>
              <h1 className="h2 mb-4">Sign in</h1>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label" htmlFor="email">
                    Email
                  </label>
                  <input
                    className="form-control"
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    autoComplete="email"
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="password">
                    Password
                  </label>
                  <input
                    className="form-control"
                    id="password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="current-password"
                    required
                  />
                </div>

                {error && (
                  <p className="alert alert-danger" role="alert">
                    {error}
                  </p>
                )}

                <button className="btn btn-primary w-100" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Signing in…" : "Sign in"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;

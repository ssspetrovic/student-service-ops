import { Link, Navigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

function NotFoundPage() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <main className="container d-flex align-items-center justify-content-center min-vh-100 py-5 text-center">
      <div>
        <p className="display-4 fw-bold text-primary mb-2">404</p>
        <h1 className="h2 mb-4">Page not found</h1>
        <Link className="btn btn-primary" to="/">
          Go home
        </Link>
      </div>
    </main>
  );
}

export default NotFoundPage;

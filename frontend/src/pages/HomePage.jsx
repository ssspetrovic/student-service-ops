import { Link, Navigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

function HomePage() {
  const { user } = useAuth();

  if (user?.role === "student") {
    return <Navigate to="/profile" replace />;
  }

  if (user?.role === "professor") {
    return <Navigate to="/professor/profile" replace />;
  }

  return (
    <main className="container py-5">
      <div className="card shadow-sm">
        <div className="card-body p-4">
          <h1 className="h2">Student Service</h1>
          {!user && (
            <Link className="btn btn-primary" to="/login">
              Log in
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}

export default HomePage;

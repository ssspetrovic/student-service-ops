import { Link, Navigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

function HomePage() {
  const { user } = useAuth();

  if (user?.role === "student") {
    return <Navigate to="/profile" replace />;
  }

  return (
    <main className="container py-5">
      <div className="card shadow-sm">
        <div className="card-body p-4">
          <h1 className="h2">Student Service</h1>
          {user ? (
            <>
              <p className="fs-5 mb-4">
                Welcome back, {user.first_name} {user.last_name}.
              </p>
            </>
          ) : (
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

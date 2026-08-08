import { Link } from "react-router-dom";
import useAuth from "../auth/useAuth";

function HomePage() {
  const { user } = useAuth();

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
              {user.role === "student" && (
                <Link className="btn btn-primary" to="/exams/available">
                  View available exams
                </Link>
              )}
            </>
          ) : (
            <Link className="btn btn-primary" to="/login">
              Sign in
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}

export default HomePage;

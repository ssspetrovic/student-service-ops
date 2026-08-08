import { Link, useNavigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-dark bg-dark">
      <div className="container-fluid px-4">
        <Link className="navbar-brand" to="/">
          Student Service
        </Link>
        <div className="d-flex align-items-center gap-3">
          {user?.role === "student" && (
            <Link className="link-light" to="/exams/available">
              Available exams
            </Link>
          )}
          {user ? (
            <>
              <span className="text-white-50 small">{user.email}</span>
              <button
                className="btn btn-primary btn-sm"
                type="button"
                onClick={handleLogout}
              >
                Log out
              </button>
            </>
          ) : (
            <Link className="btn btn-primary btn-sm" to="/login">
              Log in
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

export default AppNavbar;

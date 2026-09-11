import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

const studentLinks = [
  ["/exams/available", "Available exams"],
  ["/curriculum", "Curriculum"],
  ["/enrollments", "Enrollments"],
  ["/registrations", "Registrations"],
  ["/results", "Results"],
  ["/wallet", "Wallet"],
];

const professorLinks = [
  ["/professor/exams", "My exams"],
  ["/professor/exams/new", "Schedule exam"],
];

const adminLinks = [
  ["/admin", "Dashboard"],
  ["/admin/users", "Users"],
  ["/admin/programs", "Curricula"],
  ["/admin/courses", "Courses"],
];

const linksByRole = {
  student: studentLinks,
  professor: professorLinks,
  admin: adminLinks,
};

const profilePathByRole = {
  student: "/profile",
  professor: "/professor/profile",
};

const brandPathByRole = {
  student: "/profile",
  professor: "/professor/profile",
  admin: "/admin",
};

function AppNavbar({ theme, onToggleTheme }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);
  const accountMenuRef = useRef(null);
  const links = linksByRole[user?.role] ?? [];
  const profilePath = profilePathByRole[user?.role];
  const brandPath = brandPathByRole[user?.role] ?? "/login";

  useEffect(() => {
    const closeAccountMenu = (event) => {
      if (!accountMenuRef.current?.contains(event.target)) {
        setIsAccountMenuOpen(false);
      }
    };

    const closeOnEscape = (event) => {
      if (event.key === "Escape") {
        setIsAccountMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", closeAccountMenu);
    document.addEventListener("keydown", closeOnEscape);

    return () => {
      document.removeEventListener("mousedown", closeAccountMenu);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  const closeMenus = () => {
    setIsOpen(false);
    setIsAccountMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    closeMenus();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
      <div className="container-fluid px-4">
        <Link className="navbar-brand" to={brandPath}>
          Student Service
        </Link>
        <button
          className="navbar-toggler"
          onClick={() => {
            setIsOpen((open) => !open);
            setIsAccountMenuOpen(false);
          }}
          type="button"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div
          className={`collapse navbar-collapse${isOpen ? " show" : ""}`}
          id="main-navigation"
        >
          {user ? (
            <div className="navbar-nav ms-lg-3 me-auto">
              {links.map(([to, label]) => (
                <NavLink
                  className={({ isActive }) =>
                    `nav-link${isActive ? " active" : ""}`
                  }
                  end={to === "/admin"}
                  key={to}
                  onClick={closeMenus}
                  to={to}
                >
                  {label}
                </NavLink>
              ))}
            </div>
          ) : (
            <div className="navbar-nav ms-lg-auto">
              <Link className="nav-link" onClick={closeMenus} to="/login">
                Log in
              </Link>
              <Link className="nav-link" onClick={closeMenus} to="/register">
                Register
              </Link>
            </div>
          )}
          {user && (
            <div className="dropdown ms-lg-3" ref={accountMenuRef}>
              <button
                className="btn btn-link nav-link dropdown-toggle text-white"
                onClick={() => setIsAccountMenuOpen((open) => !open)}
                type="button"
              >
                {user.email}
              </button>
              <div
                className={`dropdown-menu dropdown-menu-end${isAccountMenuOpen ? " show" : ""}`}
              >
                {profilePath && (
                  <NavLink
                    className="dropdown-item"
                    onClick={closeMenus}
                    to={profilePath}
                  >
                    Profile
                  </NavLink>
                )}
                <button
                  className="dropdown-item"
                  onClick={handleLogout}
                  type="button"
                >
                  Log out
                </button>
              </div>
            </div>
          )}
          <button
            className="btn btn-outline-light my-2 ms-lg-3 my-lg-0"
            onClick={onToggleTheme}
            type="button"
          >
            <i
              className={
                theme === "light" ? "bi bi-moon-fill" : "bi bi-sun-fill"
              }
            />
          </button>
        </div>
      </div>
    </nav>
  );
}

export default AppNavbar;

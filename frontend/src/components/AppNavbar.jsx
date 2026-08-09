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

const linksByRole = {
  student: studentLinks,
  professor: professorLinks,
};

const profilePathByRole = {
  student: "/profile",
  professor: "/professor/profile",
};

function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);
  const accountMenuRef = useRef(null);
  const links = linksByRole[user?.role] ?? [];
  const profilePath = profilePathByRole[user?.role];

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
        <Link className="navbar-brand" to={profilePath ?? "/"}>
          Student Service
        </Link>
        <button
          aria-controls="main-navigation"
          aria-expanded={isOpen}
          aria-label="Toggle navigation"
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
            </div>
          )}
          {user && (
            <div className="dropdown ms-lg-auto" ref={accountMenuRef}>
              <button
                aria-expanded={isAccountMenuOpen}
                aria-haspopup="true"
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
        </div>
      </div>
    </nav>
  );
}

export default AppNavbar;

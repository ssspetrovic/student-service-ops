import { Link } from "react-router-dom";

const cards = [
  ["Users", "Manage student and professor accounts", "/admin/users"],
  ["Curricula", "Manage and review study programmes", "/admin/programs"],
  ["Courses", "Manage courses and assign professors", "/admin/courses"],
];

function AdminDashboardPage() {
  return (
    <main className="container py-5">
      <h1 className="h2 mb-3">Administrator dashboard</h1>
      <div className="row g-3">
        {cards.map(([title, description, to]) => (
          <div className="col-md-4" key={title}>
            <Link
              className="card h-100 border-0 shadow-sm text-decoration-none"
              to={to}
            >
              <div className="card-body d-flex flex-column p-4">
                <p className="mb-2 small text-primary text-uppercase fw-semibold">
                  Manage
                </p>
                <h2 className="h4 mb-2 text-body">{title}</h2>
                <p className="mb-4 text-body-secondary">{description}</p>
                <span className="mt-auto fw-semibold text-primary">
                  Open {title.toLowerCase()} →
                </span>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}

export default AdminDashboardPage;

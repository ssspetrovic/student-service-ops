import { Link } from "react-router-dom";

const cards = [
  ["Users", "/admin/users"],
  ["Curricula", "/admin/programs"],
  ["Courses", "/admin/courses"],
  ["New user", "/admin/users/new"],
];

function AdminDashboardPage() {
  return (
    <main className="container py-5">
      <h1 className="h2 mb-3">Administrator dashboard</h1>
      <div className="row g-3">
        {cards.map(([title, to]) => (
          <div className="col-md-6" key={title}>
            <Link className="card h-100 shadow-sm text-decoration-none" to={to}>
              <div className="card-body d-flex align-items-center justify-content-center text-center">
                <h2 className="h5 mb-0 text-body">{title}</h2>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}

export default AdminDashboardPage;

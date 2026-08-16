import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";

function roleBadgeClass(role) {
  if (role === "student") {
    return "text-bg-primary";
  }

  if (role === "professor") {
    return "text-bg-warning";
  }

  return "text-bg-dark";
}

function AdminUsersPage() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("");
  const [userToDeactivate, setUserToDeactivate] = useState(null);
  const location = useLocation();
  const [success, setSuccess] = useState(location.state?.success ?? "");

  const loadUsers = () => {
    api
      .get("/admin/users/")
      .then((response) => setUsers(response.data))
      .catch((requestError) =>
        setError(getErrorMessage(requestError, "Unable to load users.")),
      );
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const visibleUsers = [];

  for (const user of users || []) {
    const roleMatches = !role || user.role === role;
    const statusMatches = !status || String(user.is_active) === status;

    if (roleMatches && statusMatches) {
      visibleUsers.push(user);
    }
  }

  const deactivate = async () => {
    try {
      await api.post(`/admin/users/${userToDeactivate.id}/deactivate/`);
      setUserToDeactivate(null);
      setSuccess("User deactivated.");
      loadUsers();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to deactivate the user."));
    }
  };

  return (
    <main className="container py-5">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <h1 className="h2 mb-0">Users</h1>
        <Link className="btn btn-primary" to="/admin/users/new">
          New user
        </Link>
      </div>
      {error && <ErrorState message={error} />}
      <div className="row g-3 mb-3">
        <div className="col-sm-4">
          <select
            className="form-select"
            aria-label="Filter by role"
            value={role}
            onChange={(event) => setRole(event.target.value)}
          >
            <option value="">All roles</option>
            <option value="student">Students</option>
            <option value="professor">Professors</option>
            <option value="admin">Administrators</option>
          </select>
        </div>
        <div className="col-sm-4">
          <select
            className="form-select"
            aria-label="Filter by status"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
          >
            <option value="">All statuses</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
      </div>
      {!users && !error && <LoadingState label="users" />}
      {users && visibleUsers.length === 0 && (
        <EmptyState>No users match these filters.</EmptyState>
      )}
      {visibleUsers.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th className="ps-3">Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th className="pe-3" aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {visibleUsers.map((user) => (
                <tr key={user.id}>
                  <td className="ps-3">
                    {user.first_name} {user.last_name}
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span
                      className={`badge ${roleBadgeClass(user.role)} text-capitalize`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge text-bg-${user.is_active ? "success" : "secondary"}`}
                    >
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="pe-3 text-end">
                    {user.role !== "admin" && user.is_active && (
                      <>
                        <Link
                          className="btn btn-sm btn-outline-primary me-2"
                          to={`/admin/users/${user.id}/edit`}
                        >
                          Edit
                        </Link>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => setUserToDeactivate(user)}
                          type="button"
                        >
                          Deactivate
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {userToDeactivate && (
        <>
          <div className="modal-backdrop fade show" />
          <div className="modal d-block" role="dialog" aria-modal="true">
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content">
                <div className="modal-header">
                  <h2 className="h5 modal-title">Deactivate user?</h2>
                  <button
                    className="btn-close"
                    onClick={() => setUserToDeactivate(null)}
                    type="button"
                  />
                </div>
                <div className="modal-body">
                  {userToDeactivate.email} will no longer be able to sign in.
                </div>
                <div className="modal-footer">
                  <button
                    className="btn btn-outline-secondary"
                    onClick={() => setUserToDeactivate(null)}
                    type="button"
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={deactivate}
                    type="button"
                  >
                    Deactivate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
      <SuccessNotification message={success} onDismiss={() => setSuccess("")} />
    </main>
  );
}
export default AdminUsersPage;

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { ErrorState, LoadingState } from "../components/PageStates";

export function AdminUserForm({
  form,
  curricula,
  isEdit,
  submitting,
  isCreateFormValid,
  onChange,
  onSubmit,
  onValidityChange,
  className = "card shadow-sm",
}) {
  let buttonLabel = isEdit ? "Save user" : "Create user";
  if (submitting) {
    buttonLabel = isEdit ? "Saving…" : "Creating…";
  }

  return (
    <form className={className} onChange={onValidityChange} onSubmit={onSubmit}>
      <div className="card-body row g-3">
        <div className="col-md-6">
          <label className="form-label">First name</label>
          <input
            className="form-control"
            name="first_name"
            onChange={onChange}
            required
            value={form.first_name}
          />
        </div>
        <div className="col-md-6">
          <label className="form-label">Last name</label>
          <input
            className="form-control"
            name="last_name"
            onChange={onChange}
            required
            value={form.last_name}
          />
        </div>
        <div className="col-md-6">
          <label className="form-label">Email</label>
          <input
            className="form-control"
            name="email"
            onChange={onChange}
            required
            type="email"
            value={form.email}
          />
        </div>
        {!isEdit && (
          <>
            <div className="col-md-6">
              <label className="form-label">Password</label>
              <input
                className="form-control"
                name="password"
                onChange={onChange}
                required
                type="password"
                value={form.password}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">Role</label>
              <select
                className="form-select"
                name="role"
                onChange={onChange}
                value={form.role}
              >
                <option value="student">Student</option>
                <option value="professor">Professor</option>
              </select>
            </div>
          </>
        )}
        {form.role === "student" ? (
          <>
            <div className="col-md-6">
              <label className="form-label">Index number</label>
              <input
                className="form-control"
                name="index_no"
                onChange={onChange}
                required
                value={form.index_no ?? ""}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">Curriculum</label>
              <select
                className="form-select"
                name="curriculum_code"
                onChange={onChange}
                required
                value={form.curriculum_code ?? ""}
              >
                <option value="">Select a curriculum</option>
                {curricula?.map((curriculum) => (
                  <option key={curriculum.code} value={curriculum.code}>
                    {curriculum.code} — {curriculum.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-6">
              <label className="form-label">Study year</label>
              <input
                className="form-control"
                max="8"
                min="1"
                name="current_year_of_study"
                onChange={onChange}
                required
                type="number"
                value={form.current_year_of_study ?? 1}
              />
            </div>
          </>
        ) : (
          <div className="col-md-6">
            <label className="form-label">Employee number</label>
            <input
              className="form-control"
              name="employee_no"
              onChange={onChange}
              required
              value={form.employee_no ?? ""}
            />
          </div>
        )}
      </div>
      <div className="card-footer bg-transparent text-end">
        <button
          className="btn btn-primary"
          disabled={submitting || (!isEdit && !isCreateFormValid)}
          type="submit"
        >
          {buttonLabel}
        </button>
      </div>
    </form>
  );
}

function AdminUserFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [curricula, setCurricula] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const loadForm = async () => {
      try {
        const curriculaResponse = await api.get("/admin/curricula/");
        setCurricula(curriculaResponse.data);

        const users = await api.get("/admin/users/");
        const user = users.data.find((entry) => entry.id === Number(id));
        if (!user) {
          setError("User not found.");
          return;
        }

        setForm(user);
      } catch (requestError) {
        setError(getErrorMessage(requestError, "Unable to load the form."));
      }
    };

    loadForm();
  }, [id]);

  const change = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    const payload = {
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
    };

    if (form.role === "student") {
      payload.index_no = form.index_no;
      payload.curriculum_code = form.curriculum_code;
      payload.current_year_of_study = Number(form.current_year_of_study);
    } else {
      payload.employee_no = form.employee_no;
    }

    try {
      await api.patch(`/admin/users/${id}/`, payload);
      navigate("/admin/users", { state: { success: "User saved." } });
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to save the user."));
    } finally {
      setSubmitting(false);
    }
  };

  if ((!curricula || !form) && !error) {
    return <LoadingState label="the user form" />;
  }

  return (
    <main className="container py-5">
      <div className="d-flex justify-content-between mb-4">
        <h1 className="h2 mb-0">Edit user</h1>
        <Link className="btn btn-outline-secondary" to="/admin/users">
          Back to users
        </Link>
      </div>
      {error && <ErrorState message={error} />}
      {curricula && form && (
        <AdminUserForm
          curricula={curricula}
          form={form}
          isEdit
          onChange={change}
          onSubmit={submit}
          submitting={submitting}
        />
      )}
    </main>
  );
}

export default AdminUserFormPage;

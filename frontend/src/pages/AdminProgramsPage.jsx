import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";

function AdminProgramsPage() {
  const [programs, setPrograms] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);

  const load = () =>
    api
      .get("/admin/programs/")
      .then((response) => setPrograms(response.data))
      .catch((requestError) =>
        setError(getErrorMessage(requestError, "Unable to load curricula.")),
      );

  useEffect(() => {
    load();
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    setError("");
    setSubmitting(true);
    try {
      await api.post(
        "/admin/programs/",
        Object.fromEntries(new FormData(form)),
      );
      form.reset();
      setIsFormValid(false);
      setSuccess("Curriculum created.");
      load();
    } catch (requestError) {
      setError(
        getErrorMessage(requestError, "Unable to create the curriculum."),
      );
    } finally {
      setSubmitting(false);
    }
  };

  const updateFormValidity = (event) => {
    setIsFormValid(event.currentTarget.checkValidity());
  };

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">Curricula</h1>
      {error && <ErrorState message={error} />}
      <form
        className="card shadow-sm mb-4"
        onChange={updateFormValidity}
        onSubmit={submit}
      >
        <div className="card-body row g-3">
          <div className="col-md-3">
            <label className="form-label">Code</label>
            <input
              className="form-control"
              maxLength="20"
              name="code"
              required
            />
          </div>
          <div className="col-md-4">
            <label className="form-label">Name</label>
            <input
              className="form-control"
              maxLength="100"
              name="name"
              required
            />
          </div>
          <div className="col-md-3">
            <label className="form-label">Degree level</label>
            <select className="form-select" name="degree_level">
              <option value="bachelor">Bachelor</option>
              <option value="master">Master</option>
              <option value="doctoral">Doctoral</option>
            </select>
          </div>
          <div className="col-md-2">
            <label className="form-label">Duration</label>
            <input
              className="form-control"
              max="6"
              min="1"
              name="duration"
              required
              type="number"
            />
          </div>
        </div>
        <div className="card-footer bg-transparent text-end">
          <button
            className="btn btn-primary"
            disabled={submitting || !isFormValid}
            type="submit"
          >
            {submitting ? "Creating…" : "Create curriculum"}
          </button>
        </div>
      </form>
      {!programs && !error && <LoadingState label="curricula" />}
      {programs?.length === 0 && (
        <EmptyState>No curricula exist yet.</EmptyState>
      )}
      {programs?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th className="ps-3">Code</th>
                <th>Name</th>
                <th>Level</th>
                <th className="pe-3">Duration</th>
              </tr>
            </thead>
            <tbody>
              {programs.map((program) => (
                <tr key={program.id}>
                  <td className="ps-3">{program.code}</td>
                  <td>{program.name}</td>
                  <td className="text-capitalize">{program.degree_level}</td>
                  <td className="pe-3">{program.duration} years</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <SuccessNotification message={success} onDismiss={() => setSuccess("")} />
    </main>
  );
}
export default AdminProgramsPage;

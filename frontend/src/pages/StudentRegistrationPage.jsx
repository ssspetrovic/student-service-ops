import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import useAuth from "../auth/useAuth";
import { ErrorState, LoadingState } from "../components/PageStates";

function StudentRegistrationPage() {
  const { user } = useAuth();
  const [curricula, setCurricula] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/academics/curricula/")
      .then((response) => {
        if (isCurrent) setCurricula(response.data);
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(getErrorMessage(requestError, "Unable to load curricula."));
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    const form = Object.fromEntries(new FormData(event.currentTarget));
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await api.post("/auth/register/", {
        email: form.email,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        index_no: form.index_no,
        curriculum_code: form.curriculum_code,
      });
      setIsSuccessModalOpen(true);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to register."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              <p className="text-primary text-uppercase fw-semibold small">
                Student Service
              </p>
              <h1 className="h2 mb-4">Student registration</h1>
              {error && <ErrorState message={error} />}
              {!curricula && !error && <LoadingState label="curricula" />}
              {curricula && (
                <form onSubmit={handleSubmit}>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="first-name">
                        First name
                      </label>
                      <input
                        autoComplete="given-name"
                        className="form-control"
                        id="first-name"
                        name="first_name"
                        required
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="last-name">
                        Last name
                      </label>
                      <input
                        autoComplete="family-name"
                        className="form-control"
                        id="last-name"
                        name="last_name"
                        required
                      />
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="email">
                        Email
                      </label>
                      <input
                        autoComplete="email"
                        className="form-control"
                        id="email"
                        name="email"
                        required
                        type="email"
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="index-number">
                        Index number
                      </label>
                      <input
                        className="form-control"
                        id="index-number"
                        name="index_no"
                        required
                      />
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-12 mb-3">
                      <label className="form-label" htmlFor="curriculum">
                        Curriculum
                      </label>
                      <select
                        className="form-select"
                        id="curriculum"
                        name="curriculum_code"
                        required
                      >
                        <option value="">Select a curriculum</option>
                        {curricula.map((curriculum) => (
                          <option key={curriculum.code} value={curriculum.code}>
                            {curriculum.code} — {curriculum.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="password">
                        Password
                      </label>
                      <input
                        autoComplete="new-password"
                        className="form-control"
                        id="password"
                        name="password"
                        required
                        type="password"
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label" htmlFor="confirm-password">
                        Confirm password
                      </label>
                      <input
                        autoComplete="new-password"
                        className="form-control"
                        id="confirm-password"
                        name="confirmPassword"
                        required
                        type="password"
                      />
                    </div>
                  </div>
                  <button
                    className="btn btn-primary w-100"
                    disabled={isSubmitting}
                    type="submit"
                  >
                    {isSubmitting ? "Registering…" : "Register"}
                  </button>
                  <p className="mb-0 mt-3 text-center">
                    Already have an account? <Link to="/login">Log in</Link>
                  </p>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
      {isSuccessModalOpen && (
        <>
          <div
            aria-labelledby="registration-success-title"
            aria-modal="true"
            className="modal d-block"
            role="dialog"
            tabIndex="-1"
          >
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content">
                <div className="modal-header">
                  <h2
                    className="modal-title fs-5"
                    id="registration-success-title"
                  >
                    Registration successful
                  </h2>
                </div>
                <div className="modal-body">
                  <p className="mb-0">
                    Your student account has been created. You can now log in.
                  </p>
                </div>
                <div className="modal-footer">
                  <Link className="btn btn-primary" to="/login">
                    Log in
                  </Link>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop show" />
        </>
      )}
    </main>
  );
}

export default StudentRegistrationPage;

import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";
import { formatDate } from "../utils/date";

function RegistrationsPage() {
  const [registrations, setRegistrations] = useState(null);
  const [cancellableRegistrationIds, setCancellableRegistrationIds] = useState(
    new Set(),
  );
  const [error, setError] = useState("");
  const [cancellationError, setCancellationError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [registrationToCancel, setRegistrationToCancel] = useState(null);
  const [isCancelling, setIsCancelling] = useState(false);

  const loadRegistrations = async () => {
    setError("");

    try {
      const [registrationResponse, cancellableResponse] = await Promise.all([
        api.get("/exams/registrations/"),
        api.get("/exams/registrations/cancellable/"),
      ]);
      setRegistrations(registrationResponse.data);
      setCancellableRegistrationIds(
        new Set(
          cancellableResponse.data.map((registration) => registration.id),
        ),
      );
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to load your exam registrations.",
        ),
      );
    }
  };

  useEffect(() => {
    let isCurrent = true;

    Promise.all([
      api.get("/exams/registrations/"),
      api.get("/exams/registrations/cancellable/"),
    ])
      .then(([registrationResponse, cancellableResponse]) => {
        if (isCurrent) {
          setRegistrations(registrationResponse.data);
          setCancellableRegistrationIds(
            new Set(
              cancellableResponse.data.map((registration) => registration.id),
            ),
          );
        }
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(
            getErrorMessage(
              requestError,
              "Unable to load your exam registrations.",
            ),
          );
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const handleCancel = async () => {
    if (!registrationToCancel) return;

    setCancellationError("");
    setSuccessMessage("");
    setIsCancelling(true);

    try {
      await api.post(`/exams/registrations/${registrationToCancel.id}/cancel/`);
      setRegistrationToCancel(null);
      setSuccessMessage("Exam registration canceled.");
      await loadRegistrations();
    } catch (requestError) {
      setCancellationError(
        getErrorMessage(
          requestError,
          "Unable to cancel this exam registration.",
        ),
      );
    } finally {
      setIsCancelling(false);
    }
  };

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My exam registrations</h1>
      {error && <ErrorState message={error} />}
      {cancellationError && <ErrorState message={cancellationError} />}
      {!registrations && !error && (
        <LoadingState label="your exam registrations" />
      )}
      {registrations?.length === 0 && (
        <EmptyState>You have no exam registrations.</EmptyState>
      )}
      {registrations?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th className="ps-3">Course</th>
                <th>Date</th>
                <th>Room</th>
                <th>Status</th>
                <th>Grade</th>
                <th className="pe-3">
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {registrations.map((registration) => (
                <tr key={registration.id}>
                  <td className="ps-3">
                    <strong>{registration.exam_course_code}</strong>
                    <br />
                    <span className="text-body-secondary">
                      {registration.exam_course_name}
                    </span>
                  </td>
                  <td>{formatDate(registration.exam_date)}</td>
                  <td>{registration.exam_room || "—"}</td>
                  <td className="text-capitalize">{registration.status}</td>
                  <td>{registration.grade ?? "—"}</td>
                  <td className="pe-3 text-end">
                    {cancellableRegistrationIds.has(registration.id) && (
                      <button
                        className="btn btn-outline-danger btn-sm"
                        disabled={isCancelling}
                        onClick={() => {
                          setCancellationError("");
                          setRegistrationToCancel(registration);
                        }}
                        type="button"
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <SuccessNotification
        message={successMessage}
        onDismiss={() => setSuccessMessage("")}
      />

      {registrationToCancel && (
        <div
          aria-labelledby="cancel-registration-title"
          aria-modal="true"
          className="modal d-block"
          role="dialog"
          tabIndex="-1"
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title fs-5" id="cancel-registration-title">
                  Cancel exam registration?
                </h2>
                <button
                  aria-label="Close"
                  className="btn-close"
                  disabled={isCancelling}
                  onClick={() => setRegistrationToCancel(null)}
                  type="button"
                />
              </div>
              <div className="modal-body">
                <p className="mb-0">
                  Cancel your registration for{" "}
                  {registrationToCancel.exam_course_code}? The registration fee
                  will be refunded to your wallet.
                </p>
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-outline-secondary"
                  disabled={isCancelling}
                  onClick={() => setRegistrationToCancel(null)}
                  type="button"
                >
                  Keep registration
                </button>
                <button
                  className="btn btn-danger"
                  disabled={isCancelling}
                  onClick={handleCancel}
                  type="button"
                >
                  {isCancelling ? (
                    <>
                      <span
                        aria-hidden="true"
                        className="spinner-border spinner-border-sm me-2"
                      />
                      Canceling
                    </>
                  ) : (
                    "Cancel registration"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {registrationToCancel && <div className="modal-backdrop show" />}
    </main>
  );
}

export default RegistrationsPage;

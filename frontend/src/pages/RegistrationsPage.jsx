import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function formatDate(date) {
  return new Date(date).toLocaleString();
}

function RegistrationsPage() {
  const [registrations, setRegistrations] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/exams/registrations/")
      .then((response) => {
        if (isCurrent) setRegistrations(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(
              requestError,
              "Unable to load your exam registrations.",
            ),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My exam registrations</h1>
      {error && <ErrorState message={error} />}
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
                <th>Course</th>
                <th>Date</th>
                <th>Room</th>
                <th>Status</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              {registrations.map((registration) => (
                <tr key={registration.id}>
                  <td>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

export default RegistrationsPage;

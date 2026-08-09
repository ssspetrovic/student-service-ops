import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function EnrollmentsPage() {
  const [enrollments, setEnrollments] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/academics/enrollments/")
      .then((response) => {
        if (isCurrent) setEnrollments(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(requestError, "Unable to load your enrollments."),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My enrollments</h1>
      {error && <ErrorState message={error} />}
      {!enrollments && !error && <LoadingState label="your enrollments" />}
      {enrollments?.length === 0 && (
        <EmptyState>You have no course enrollments.</EmptyState>
      )}
      {enrollments?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th className="ps-3">Course</th>
                <th>ESPB</th>
                <th>Semester</th>
                <th>School year</th>
                <th className="pe-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {enrollments.map((enrollment) => (
                <tr key={`${enrollment.course_code}-${enrollment.school_year}`}>
                  <td className="ps-3">
                    <strong>{enrollment.course_code}</strong>
                    <br />
                    <span className="text-body-secondary">
                      {enrollment.course_name}
                    </span>
                  </td>
                  <td>{enrollment.course_espb}</td>
                  <td>{enrollment.semester}</td>
                  <td>{enrollment.school_year}</td>
                  <td className="pe-3 text-capitalize">{enrollment.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

export default EnrollmentsPage;

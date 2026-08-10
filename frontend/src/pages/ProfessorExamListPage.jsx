import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";
import { formatDate, isFinished } from "../utils/date";

function ProfessorExamListPage() {
  const [exams, setExams] = useState(null);
  const [error, setError] = useState("");
  const location = useLocation();
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState(
    () => location.state?.successMessage ?? "",
  );

  useEffect(() => {
    if (location.state?.successMessage) {
      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, navigate]);

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/exams/mine/")
      .then((response) => {
        if (isCurrent) setExams(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(getErrorMessage(requestError, "Unable to load your exams."));
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <h1 className="h2 mb-0">My scheduled exams</h1>
        <Link className="btn btn-primary" to="/professor/exams/new">
          Schedule exam
        </Link>
      </div>
      {error && <ErrorState message={error} />}
      {!exams && !error && <LoadingState label="your scheduled exams" />}
      {exams?.length === 0 && (
        <EmptyState>You have no scheduled exams.</EmptyState>
      )}
      {exams?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th className="ps-3">Course</th>
                <th>Date</th>
                <th>Room</th>
                <th>Status</th>
                <th className="pe-3">
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.id}>
                  <td className="ps-3">
                    <strong>{exam.course_code}</strong>
                    <br />
                    <span className="text-body-secondary">
                      {exam.course_name}
                    </span>
                  </td>
                  <td>{formatDate(exam.date)}</td>
                  <td>{exam.room || "—"}</td>
                  <td>
                    <span
                      className={`badge text-bg-${isFinished(exam.date) ? "success" : "primary"}`}
                    >
                      {isFinished(exam.date) ? "Finished" : "Upcoming"}
                    </span>
                  </td>
                  <td className="pe-3 text-end">
                    <Link
                      className="btn btn-outline-primary btn-sm"
                      to={`/professor/exams/${exam.id}/registrations`}
                    >
                      Registrations
                    </Link>
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
    </main>
  );
}

export default ProfessorExamListPage;

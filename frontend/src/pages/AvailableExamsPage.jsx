import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { ErrorState, LoadingState } from "../components/PageStates";

function formatExamDate(date) {
  return new Date(date).toLocaleString();
}

function AvailableExamsPage() {
  const [exams, setExams] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCurrent = true;

    const loadExams = async () => {
      try {
        const response = await api.get("/exams/available/");

        if (isCurrent) {
          setExams(response.data);
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(getErrorMessage(requestError, "Unable to load available exams."));
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    };

    loadExams();

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">Available exams</h1>

      {isLoading && (
        <LoadingState label="available exams" />
      )}

      {error && (
        <ErrorState message={error} />
      )}

      {!isLoading && !error && exams.length === 0 && (
        <p className="alert alert-info" role="status">
          No exams are currently available for registration.
        </p>
      )}

      {!isLoading && !error && exams.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th scope="col">Course</th>
                <th scope="col">Date</th>
                <th scope="col">Room</th>
                <th scope="col">Professor</th>
                <th scope="col">Fee</th>
              </tr>
            </thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.id}>
                  <td>
                    <strong>{exam.course_code}</strong>
                    <br />
                    <span className="text-body-secondary">
                      {exam.course_name}
                    </span>
                  </td>
                  <td>{formatExamDate(exam.date)}</td>
                  <td>{exam.room || "—"}</td>
                  <td>{exam.professor_email}</td>
                  <td>{exam.registration_fee} RSD</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

export default AvailableExamsPage;

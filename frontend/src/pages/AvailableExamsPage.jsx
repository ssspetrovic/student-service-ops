import { useEffect, useState } from "react";
import api from "../api/client";

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
          setError(
            requestError.response?.data?.detail ||
              "Unable to load available exams.",
          );
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
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading available exams</span>
          </div>
        </div>
      )}

      {error && (
        <p className="alert alert-danger" role="alert">
          {error}
        </p>
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

import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function formatDate(date) {
  return new Date(date).toLocaleString();
}

function ResultsPage() {
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/exams/results/")
      .then((response) => {
        if (isCurrent) setResultData(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(requestError, "Unable to load your results."),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My results</h1>
      {error && <ErrorState message={error} />}
      {!resultData && !error && <LoadingState label="your results" />}
      {resultData && (
        <>
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5">Passing-grade average</h2>
              <p className="display-6 mb-0">{resultData.average ?? "—"}</p>
            </div>
          </div>
          {resultData.results.length === 0 ? (
            <EmptyState>You have no graded exam results.</EmptyState>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped align-middle">
                <thead>
                  <tr>
                    <th className="ps-3">Course</th>
                    <th>Exam date</th>
                    <th className="pe-3">Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {resultData.results.map((result) => (
                    <tr key={result.id}>
                      <td className="ps-3">
                        <strong>{result.exam_course_code}</strong>
                        <br />
                        <span className="text-body-secondary">
                          {result.exam_course_name}
                        </span>
                      </td>
                      <td>{formatDate(result.exam_date)}</td>
                      <td className="pe-3">{result.grade}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </main>
  );
}

export default ResultsPage;

import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function ProfessorExamCreatePage() {
  const [courses, setCourses] = useState(null);
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [searchParams] = useSearchParams();
  const [courseCode, setCourseCode] = useState(
    () => searchParams.get("course") ?? "",
  );
  const [date, setDate] = useState("");
  const [room, setRoom] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/academics/my-courses/")
      .then((response) => {
        if (isCurrent) setCourses(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(
              requestError,
              "Unable to load your assigned courses.",
            ),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitError("");
    setIsSubmitting(true);

    try {
      await api.post("/exams/", {
        course_code: courseCode,
        date: new Date(date).toISOString(),
        room,
      });
      navigate("/professor/exams", {
        state: { successMessage: "Exam scheduled." },
      });
    } catch (requestError) {
      setSubmitError(
        getErrorMessage(requestError, "Unable to schedule this exam."),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="container py-5">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <h1 className="h2 mb-0">Schedule exam</h1>
        <Link className="btn btn-outline-secondary" to="/professor/exams">
          Back to exams
        </Link>
      </div>
      {error && <ErrorState message={error} />}
      {submitError && <ErrorState message={submitError} />}
      {!courses && !error && <LoadingState label="your assigned courses" />}
      {courses?.length === 0 && (
        <EmptyState>
          You have no assigned courses available for scheduling.
        </EmptyState>
      )}
      {courses?.length > 0 && (
        <form className="card shadow-sm" onSubmit={handleSubmit}>
          <div className="card-body row gy-3">
            <div className="col-md-6">
              <label className="form-label" htmlFor="course-code">
                Course
              </label>
              <select
                className="form-select"
                id="course-code"
                onChange={(event) => setCourseCode(event.target.value)}
                required
                value={courseCode}
              >
                <option value="">Select a course</option>
                {courses.map((course) => (
                  <option key={course.code} value={course.code}>
                    {course.code} — {course.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-6">
              <label className="form-label" htmlFor="exam-date">
                Date and time
              </label>
              <input
                className="form-control"
                id="exam-date"
                onChange={(event) => setDate(event.target.value)}
                required
                type="datetime-local"
                value={date}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label" htmlFor="exam-room">
                Room <span className="text-body-secondary">(optional)</span>
              </label>
              <input
                className="form-control"
                id="exam-room"
                maxLength="50"
                onChange={(event) => setRoom(event.target.value)}
                value={room}
              />
            </div>
          </div>
          <div className="card-footer bg-transparent text-end">
            <button
              className="btn btn-primary"
              disabled={isSubmitting || !courseCode}
              type="submit"
            >
              {isSubmitting ? "Scheduling exam…" : "Schedule exam"}
            </button>
          </div>
        </form>
      )}
    </main>
  );
}

export default ProfessorExamCreatePage;

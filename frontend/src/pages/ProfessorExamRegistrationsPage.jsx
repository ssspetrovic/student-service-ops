import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";
import { formatDate, isFinished } from "../utils/date";

const gradeOptions = [5, 6, 7, 8, 9, 10];

async function fetchExam(examId) {
  const [examResponse, registrationResponse] = await Promise.all([
    api.get("/exams/mine/"),
    api.get(`/exams/${examId}/registrations/`),
  ]);

  return {
    exam: examResponse.data.find(
      (candidate) => candidate.id === Number(examId),
    ),
    registrations: registrationResponse.data,
  };
}

function ProfessorExamRegistrationsPage() {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [registrations, setRegistrations] = useState(null);
  const [error, setError] = useState("");
  const [registrationToGrade, setRegistrationToGrade] = useState(null);
  const [grade, setGrade] = useState(5);
  const [gradeError, setGradeError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    let isCurrent = true;

    fetchExam(examId)
      .then(({ exam: selectedExam, registrations: loadedRegistrations }) => {
        if (!isCurrent) return;
        if (!selectedExam) {
          setError("This exam is not available for grading.");
          return;
        }

        setExam(selectedExam);
        setRegistrations(loadedRegistrations);
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(
            getErrorMessage(
              requestError,
              "Unable to load this exam and its registrations.",
            ),
          );
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [examId]);

  const openGradeModal = (registration) => {
    setRegistrationToGrade(registration);
    setGrade(registration.grade ?? 5);
    setGradeError("");
    setSuccessMessage("");
  };

  const closeGradeModal = () => {
    if (!isSaving) setRegistrationToGrade(null);
  };

  const handleGrade = async (event) => {
    event.preventDefault();
    if (!registrationToGrade) return;

    setGradeError("");
    setIsSaving(true);

    try {
      await api.patch(`/exams/registrations/${registrationToGrade.id}/grade/`, {
        grade,
      });
      const registrationResponse = await api.get(
        `/exams/${examId}/registrations/`,
      );
      setRegistrations(registrationResponse.data);
      setRegistrationToGrade(null);
      setSuccessMessage("Grade saved successfully.");
    } catch (requestError) {
      setGradeError(
        getErrorMessage(requestError, "Unable to save this grade."),
      );
    } finally {
      setIsSaving(false);
    }
  };

  const canGrade = exam && isFinished(exam.date);

  return (
    <main className="container py-5">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <h1 className="h2 mb-0">Exam grading</h1>
        <Link className="btn btn-outline-secondary" to="/professor/exams">
          Back to exams
        </Link>
      </div>
      {error && <ErrorState message={error} />}
      {(!exam || !registrations) && !error && (
        <LoadingState label="this exam and its registrations" />
      )}
      {exam && registrations && (
        <>
          <section
            aria-labelledby="selected-exam-title"
            className="card shadow-sm mb-4"
          >
            <div className="card-body">
              <h2 className="h4" id="selected-exam-title">
                {exam.course_code} — {exam.course_name}
              </h2>
              <dl className="row mb-0">
                <dt className="col-sm-3">Exam date</dt>
                <dd className="col-sm-9 mb-2">{formatDate(exam.date)}</dd>
                <dt className="col-sm-3">Room</dt>
                <dd className="col-sm-9 mb-2">{exam.room || "—"}</dd>
                <dt className="col-sm-3">Status</dt>
                <dd className="col-sm-9 mb-0">
                  <span
                    className={`badge text-bg-${canGrade ? "success" : "primary"}`}
                  >
                    {canGrade ? "Finished" : "Upcoming"}
                  </span>
                </dd>
              </dl>
            </div>
          </section>
          <h2 className="h4 mb-3">Registered students</h2>
          {registrations.length === 0 ? (
            <EmptyState>
              There are no active registrations for this exam.
            </EmptyState>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped align-middle">
                <thead>
                  <tr>
                    <th className="ps-3">Student</th>
                    <th>Index number</th>
                    <th>Status</th>
                    <th>Current grade</th>
                    <th className="pe-3">
                      <span className="visually-hidden">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {registrations.map((registration) => (
                    <tr key={registration.id}>
                      <td className="ps-3">{registration.student_name}</td>
                      <td>{registration.student_index_no}</td>
                      <td className="text-capitalize">{registration.status}</td>
                      <td>{registration.grade ?? "—"}</td>
                      <td className="pe-3 text-end">
                        <button
                          className="btn btn-outline-primary btn-sm"
                          disabled={!canGrade}
                          onClick={() => openGradeModal(registration)}
                          type="button"
                        >
                          {canGrade
                            ? registration.grade === null
                              ? "Enter grade"
                              : "Change grade"
                            : "Available after exam"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
      <SuccessNotification
        message={successMessage}
        onDismiss={() => setSuccessMessage("")}
      />

      {registrationToGrade && exam && <div className="modal-backdrop show" />}
      {registrationToGrade && exam && (
        <div
          aria-labelledby="grade-registration-title"
          aria-modal="true"
          className="modal d-block"
          role="dialog"
          tabIndex="-1"
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title fs-5" id="grade-registration-title">
                  Grade {registrationToGrade.student_name}
                </h2>
                <button
                  aria-label="Close"
                  className="btn-close"
                  disabled={isSaving}
                  onClick={closeGradeModal}
                  type="button"
                />
              </div>
              <form onSubmit={handleGrade}>
                <div className="modal-body">
                  <p>
                    {exam.course_code} — {exam.course_name}
                  </p>
                  <p className="mb-3">
                    {registrationToGrade.student_name} (
                    {registrationToGrade.student_index_no})
                  </p>
                  <label className="form-label" htmlFor="exam-grade">
                    Grade
                  </label>
                  <select
                    className="form-select"
                    disabled={isSaving}
                    id="exam-grade"
                    onChange={(event) => setGrade(Number(event.target.value))}
                    value={grade}
                  >
                    {gradeOptions.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                  {gradeError && (
                    <div className="mt-3">
                      <ErrorState message={gradeError} />
                    </div>
                  )}
                </div>
                <div className="modal-footer">
                  <button
                    className="btn btn-outline-secondary"
                    disabled={isSaving}
                    onClick={closeGradeModal}
                    type="button"
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-primary"
                    disabled={isSaving}
                    type="submit"
                  >
                    {isSaving ? "Saving…" : "Save grade"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default ProfessorExamRegistrationsPage;

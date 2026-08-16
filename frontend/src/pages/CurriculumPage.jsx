import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function CurriculumPage() {
  const [curriculum, setCurriculum] = useState(null);
  const [error, setError] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("all");

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/academics/my-curriculum/")
      .then((response) => {
        if (isCurrent) setCurriculum(response.data);
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(requestError, "Unable to load your curriculum."),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const courses =
    curriculum?.courses?.filter(
      (course) =>
        selectedSemester === "all" ||
        course.semester === Number(selectedSemester),
    ) ?? [];
  const semesters = curriculum
    ? Array.from({ length: curriculum.duration * 2 }, (_, index) => index + 1)
    : [];

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My curriculum</h1>
      {error && <ErrorState message={error} />}
      {!curriculum && !error && <LoadingState label="your curriculum" />}
      {curriculum && (
        <>
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h4">{curriculum.name}</h2>
              <p className="mb-0 text-body-secondary">
                {curriculum.code} · {curriculum.degree_level} ·{" "}
                {curriculum.duration} years
              </p>
            </div>
          </div>
          <div className="mb-4 col-sm-5 col-md-4">
            <label className="form-label" htmlFor="semester">
              Semester
            </label>
            <select
              className="form-select"
              id="semester"
              onChange={(event) => setSelectedSemester(event.target.value)}
              value={selectedSemester}
            >
              <option value="all">All semesters</option>
              {semesters.map((semester) => (
                <option key={semester} value={semester}>
                  Semester {semester}
                </option>
              ))}
            </select>
          </div>
          {courses.length === 0 ? (
            <EmptyState>
              {selectedSemester === "all"
                ? "No courses are assigned to this curriculum."
                : "No courses are assigned to this semester."}
            </EmptyState>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped align-middle">
                <thead>
                  <tr>
                    <th className="ps-3">Semester</th>
                    <th>Course</th>
                    <th>ESPB</th>
                    <th>Professor</th>
                    <th className="pe-3">Type</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((course) => (
                    <tr key={course.code}>
                      <td className="ps-3">{course.semester}</td>
                      <td>
                        <strong>{course.code}</strong>
                        <br />
                        <span className="text-body-secondary">
                          {course.name}
                        </span>
                      </td>
                      <td>{course.espb}</td>
                      <td>{course.professor_email}</td>
                      <td className="pe-3">
                        {course.is_mandatory ? "Mandatory" : "Elective"}
                      </td>
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

export default CurriculumPage;

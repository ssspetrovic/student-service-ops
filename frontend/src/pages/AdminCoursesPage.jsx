import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";

function AdminCoursesPage() {
  const [courses, setCourses] = useState(null);
  const [professors, setProfessors] = useState(null);
  const [selected, setSelected] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(null);

  const load = () =>
    Promise.all([api.get("/admin/courses/"), api.get("/admin/professors/")])
      .then(([courseResponse, professorResponse]) => {
        setCourses(courseResponse.data);
        setProfessors(professorResponse.data);
        const selectedProfessors = {};
        for (const course of courseResponse.data) {
          selectedProfessors[course.id] = String(course.professor_id);
        }
        setSelected(selectedProfessors);
      })
      .catch((requestError) =>
        setError(getErrorMessage(requestError, "Unable to load courses.")),
      );

  useEffect(() => {
    load();
  }, []);

  const save = async (course) => {
    setSaving(course.id);
    setError("");
    try {
      await api.patch(`/admin/courses/${course.id}/`, {
        professor_id: Number(selected[course.id]),
      });
      setSuccess("Course assignment saved.");
      load();
    } catch (requestError) {
      setError(
        getErrorMessage(requestError, "Unable to assign the professor."),
      );
    } finally {
      setSaving(null);
    }
  };

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">Course assignments</h1>
      {error && <ErrorState message={error} />}
      {(!courses || !professors) && !error && <LoadingState label="courses" />}
      {courses?.length === 0 && <EmptyState>No courses exist yet.</EmptyState>}
      {courses?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped align-middle">
            <thead>
              <tr>
                <th className="ps-3">Code</th>
                <th>Course</th>
                <th>ESPB</th>
                <th>Professor</th>
                <th className="pe-3" aria-label="Save" />
              </tr>
            </thead>
            <tbody>
              {courses.map((course) => (
                <tr key={course.id}>
                  <td className="ps-3">{course.code}</td>
                  <td>{course.name}</td>
                  <td>{course.espb}</td>
                  <td>
                    <select
                      className="form-select"
                      onChange={(event) =>
                        setSelected((current) => ({
                          ...current,
                          [course.id]: event.target.value,
                        }))
                      }
                      value={selected[course.id] ?? ""}
                    >
                      {professors?.map((professor) => (
                        <option key={professor.id} value={professor.id}>
                          {professor.first_name} {professor.last_name} (
                          {professor.employee_no})
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="pe-3 text-end">
                    <button
                      className="btn btn-sm btn-primary"
                      disabled={saving === course.id}
                      onClick={() => save(course)}
                      type="button"
                    >
                      Save
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <SuccessNotification message={success} onDismiss={() => setSuccess("")} />
    </main>
  );
}
export default AdminCoursesPage;

import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";

const initialCourseForm = {
  code: "",
  name: "",
  espb: 6,
  professor_id: "",
  curriculum_code: "",
  semester: 1,
  is_mandatory: true,
};

const courseFields = [
  { column: "col-md-4", label: "Course code", name: "code" },
  { column: "col-md-8", label: "Course name", name: "name" },
  {
    column: "col-md-3",
    label: "ESPB",
    max: "60",
    min: "1",
    name: "espb",
    type: "number",
  },
  {
    column: "col-md-3",
    label: "Semester",
    max: "12",
    min: "1",
    name: "semester",
    type: "number",
  },
];

function AdminCoursesPage() {
  const [courses, setCourses] = useState(null);
  const [professors, setProfessors] = useState(null);
  const [curricula, setCurricula] = useState(null);
  const [selected, setSelected] = useState({});
  const [form, setForm] = useState(initialCourseForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(null);
  const [creating, setCreating] = useState(false);

  const load = () =>
    Promise.all([
      api.get("/admin/courses/"),
      api.get("/admin/professors/"),
      api.get("/admin/programs/"),
    ])
      .then(([courseResponse, professorResponse, curriculumResponse]) => {
        setCourses(courseResponse.data);
        setProfessors(professorResponse.data);
        setCurricula(curriculumResponse.data);
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

  const changeForm = (event) => {
    const { name, type, checked, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const createCourse = async (event) => {
    event.preventDefault();
    setCreating(true);
    setError("");
    try {
      await api.post("/admin/courses/", {
        ...form,
        espb: Number(form.espb),
        professor_id: Number(form.professor_id),
        semester: Number(form.semester),
      });
      setForm(initialCourseForm);
      setSuccess("Course created.");
      load();
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to create the course."));
    } finally {
      setCreating(false);
    }
  };

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">Course assignments</h1>
      {error && <ErrorState message={error} />}
      {(!courses || !professors || !curricula) && !error && (
        <LoadingState label="courses" />
      )}
      {courses && professors && curricula && (
        <form className="card shadow-sm mb-4" onSubmit={createCourse}>
          <div className="card-body row g-3">
            {courseFields
              .slice(0, 3)
              .map(({ column, label, name, ...input }) => (
                <div className={column} key={name}>
                  <label className="form-label" htmlFor={`course-${name}`}>
                    {label}
                  </label>
                  <input
                    {...input}
                    className="form-control"
                    id={`course-${name}`}
                    name={name}
                    onChange={changeForm}
                    required
                    value={form[name]}
                  />
                </div>
              ))}
            <div className="col-md-5">
              <label className="form-label" htmlFor="course-professor">
                Professor
              </label>
              <select
                className="form-select"
                id="course-professor"
                name="professor_id"
                onChange={changeForm}
                required
                value={form.professor_id}
              >
                <option value="">Select a professor</option>
                {professors.map((professor) => (
                  <option key={professor.id} value={professor.id}>
                    {professor.first_name} {professor.last_name} (
                    {professor.employee_no})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label" htmlFor="course-curriculum">
                Curriculum
              </label>
              <select
                className="form-select"
                id="course-curriculum"
                name="curriculum_code"
                onChange={changeForm}
                required
                value={form.curriculum_code}
              >
                <option value="">Select a curriculum</option>
                {curricula.map((curriculum) => (
                  <option key={curriculum.code} value={curriculum.code}>
                    {curriculum.code} — {curriculum.name}
                  </option>
                ))}
              </select>
            </div>
            {courseFields.slice(3).map(({ column, label, name, ...input }) => (
              <div className={column} key={name}>
                <label className="form-label" htmlFor={`course-${name}`}>
                  {label}
                </label>
                <input
                  {...input}
                  className="form-control"
                  id={`course-${name}`}
                  name={name}
                  onChange={changeForm}
                  required
                  value={form[name]}
                />
              </div>
            ))}
            <div className="col-md-4 d-flex align-items-end">
              <div className="form-check mb-2">
                <input
                  checked={form.is_mandatory}
                  className="form-check-input"
                  id="course-mandatory"
                  name="is_mandatory"
                  onChange={changeForm}
                  type="checkbox"
                />
                <label className="form-check-label" htmlFor="course-mandatory">
                  Mandatory course
                </label>
              </div>
            </div>
          </div>
          <div className="card-footer bg-transparent text-end">
            <button
              className="btn btn-primary"
              disabled={creating}
              type="submit"
            >
              {creating ? "Creating…" : "Create course"}
            </button>
          </div>
        </form>
      )}
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

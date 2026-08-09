import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function ProfessorProfilePage() {
  const [profile, setProfile] = useState(null);
  const [courses, setCourses] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    Promise.all([
      api.get("/accounts/professor-profile/"),
      api.get("/academics/my-courses/"),
    ])
      .then(([profileResponse, coursesResponse]) => {
        if (!isCurrent) return;
        setProfile(profileResponse.data);
        setCourses(coursesResponse.data);
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(
            getErrorMessage(requestError, "Unable to load your profile."),
          );
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My profile</h1>
      {error && <ErrorState message={error} />}
      {(!profile || !courses) && !error && (
        <LoadingState label="your profile" />
      )}
      {profile && courses && (
        <>
          <div className="card shadow-sm mb-4">
            <dl className="row card-body mb-0">
              <dt className="col-sm-4">Name</dt>
              <dd className="col-sm-8">
                {profile.first_name} {profile.last_name}
              </dd>
              <dt className="col-sm-4">Email</dt>
              <dd className="col-sm-8">{profile.email}</dd>
              <dt className="col-sm-4">Employee number</dt>
              <dd className="col-sm-8">{profile.employee_no}</dd>
            </dl>
          </div>
          <section aria-labelledby="courses-title">
            <h2 className="h4 mb-3" id="courses-title">
              My courses
            </h2>
            {courses.length === 0 ? (
              <EmptyState>You have no assigned courses.</EmptyState>
            ) : (
              <div className="table-responsive">
                <table className="table table-striped align-middle">
                  <thead>
                    <tr>
                      <th className="ps-3">Semester</th>
                      <th>Code</th>
                      <th>Course</th>
                      <th>ESPB</th>
                      <th className="pe-3">
                        <span className="visually-hidden">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {courses.map((course) => (
                      <tr key={course.code}>
                        <td className="ps-3">{course.semesters.join(", ")}</td>
                        <td>
                          <strong>{course.code}</strong>
                        </td>
                        <td>{course.name}</td>
                        <td>{course.espb}</td>
                        <td className="pe-3 text-end">
                          <Link
                            className="btn btn-primary btn-sm"
                            to={`/professor/exams/new?course=${course.code}`}
                          >
                            Schedule exam
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}

export default ProfessorProfilePage;

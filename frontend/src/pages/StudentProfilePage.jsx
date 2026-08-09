import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { ErrorState, LoadingState } from "../components/PageStates";

function StudentProfilePage() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    api.get("/accounts/student-profile/")
      .then((response) => {
        if (isCurrent) setProfile(response.data);
      })
      .catch((requestError) => {
        if (isCurrent) setError(getErrorMessage(requestError, "Unable to load your profile."));
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My profile</h1>
      {error && <ErrorState message={error} />}
      {!profile && !error && <LoadingState label="your profile" />}
      {profile && (
        <div className="card shadow-sm">
          <dl className="row card-body mb-0">
            <dt className="col-sm-4">Name</dt>
            <dd className="col-sm-8">{profile.first_name} {profile.last_name}</dd>
            <dt className="col-sm-4">Email</dt>
            <dd className="col-sm-8">{profile.email}</dd>
            <dt className="col-sm-4">Index number</dt>
            <dd className="col-sm-8">{profile.index_no}</dd>
            <dt className="col-sm-4">Year of study</dt>
            <dd className="col-sm-8">{profile.current_year_of_study}</dd>
            <dt className="col-sm-4">Programme</dt>
            <dd className="col-sm-8">{profile.curriculum_name} ({profile.curriculum_code})</dd>
          </dl>
        </div>
      )}
    </main>
  );
}

export default StudentProfilePage;

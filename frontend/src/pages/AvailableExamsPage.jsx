import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";

function formatExamDate(date) {
  return new Date(date).toLocaleString();
}

function AvailableExamsPage() {
  const [exams, setExams] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [registrationError, setRegistrationError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [examToRegister, setExamToRegister] = useState(null);
  const [walletBalance, setWalletBalance] = useState(null);
  const [walletError, setWalletError] = useState("");
  const [isLoadingWallet, setIsLoadingWallet] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);

  const loadExams = async () => {
    setError("");

    try {
      const response = await api.get("/exams/available/");
      setExams(response.data);
    } catch (requestError) {
      setError(
        getErrorMessage(requestError, "Unable to load available exams."),
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isCurrent = true;

    api
      .get("/exams/available/")
      .then((response) => {
        if (isCurrent) setExams(response.data);
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(
            getErrorMessage(requestError, "Unable to load available exams."),
          );
        }
      })
      .finally(() => {
        if (isCurrent) setIsLoading(false);
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const openRegistrationConfirmation = async (exam) => {
    setRegistrationError("");
    setSuccessMessage("");
    setExamToRegister(exam);
    setWalletBalance(null);
    setWalletError("");
    setIsLoadingWallet(true);

    try {
      const response = await api.get("/finance/wallet/");
      setWalletBalance(response.data.balance);
    } catch (requestError) {
      setWalletError(
        getErrorMessage(requestError, "Unable to load your wallet."),
      );
    } finally {
      setIsLoadingWallet(false);
    }
  };

  const closeRegistrationConfirmation = () => {
    if (!isRegistering) setExamToRegister(null);
  };

  const handleRegister = async () => {
    if (!examToRegister) return;

    setRegistrationError("");
    setIsRegistering(true);

    try {
      await api.post(`/exams/${examToRegister.id}/register/`);
      setExamToRegister(null);
      setSuccessMessage("Exam registration completed successfully.");
      await loadExams();
    } catch (requestError) {
      setRegistrationError(
        getErrorMessage(requestError, "Unable to register for this exam."),
      );
    } finally {
      setIsRegistering(false);
    }
  };

  const canAffordRegistration =
    examToRegister &&
    walletBalance !== null &&
    Number(walletBalance) >= Number(examToRegister.registration_fee);
  const balanceAfterRegistration =
    canAffordRegistration &&
    (Number(walletBalance) - Number(examToRegister.registration_fee)).toFixed(
      2,
    );

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">Available exams</h1>

      {registrationError && !examToRegister && (
        <ErrorState message={registrationError} />
      )}

      {isLoading && <LoadingState label="available exams" />}

      {error && <ErrorState message={error} />}

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
                <th className="ps-3" scope="col">
                  Course
                </th>
                <th scope="col">Date</th>
                <th scope="col">Room</th>
                <th scope="col">Professor</th>
                <th scope="col">Fee</th>
                <th className="pe-3" scope="col">
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.id}>
                  <td className="ps-3">
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
                  <td className="pe-3 text-end">
                    <button
                      className="btn btn-primary btn-sm"
                      disabled={isRegistering}
                      onClick={() => openRegistrationConfirmation(exam)}
                      type="button"
                    >
                      Register
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <SuccessNotification
        message={successMessage}
        onDismiss={() => setSuccessMessage("")}
      />

      {examToRegister && (
        <div
          aria-labelledby="register-exam-title"
          aria-modal="true"
          className="modal d-block"
          role="dialog"
          tabIndex="-1"
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h2 className="modal-title fs-5" id="register-exam-title">
                  Confirm exam registration
                </h2>
                <button
                  aria-label="Close"
                  className="btn-close"
                  disabled={isRegistering}
                  onClick={closeRegistrationConfirmation}
                  type="button"
                />
              </div>
              <div className="modal-body">
                <p>
                  Register for {examToRegister.course_code} —{" "}
                  {examToRegister.course_name}?
                </p>
                {isLoadingWallet && (
                  <LoadingState label="your current balance" />
                )}
                {walletError && <ErrorState message={walletError} />}
                {walletBalance !== null && (
                  <dl className="row mb-0">
                    <dt className="col-sm-6">Current balance</dt>
                    <dd className="col-sm-6">{walletBalance} RSD</dd>
                    <dt className="col-sm-6">Registration fee</dt>
                    <dd className="col-sm-6">
                      {examToRegister.registration_fee} RSD
                    </dd>
                    {balanceAfterRegistration && (
                      <>
                        <div className="col-12">
                          <hr className="my-2" />
                        </div>
                        <dt className="col-sm-6">Balance after registration</dt>
                        <dd className="col-sm-6">
                          {balanceAfterRegistration} RSD
                        </dd>
                      </>
                    )}
                  </dl>
                )}
                {!isLoadingWallet &&
                  walletBalance !== null &&
                  !canAffordRegistration && (
                    <p className="alert alert-warning mb-0 mt-3" role="alert">
                      Insufficient funds. You can{" "}
                      <Link to="/wallet">add funds</Link> in your wallet.
                    </p>
                  )}
                {registrationError && (
                  <ErrorState message={registrationError} />
                )}
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-outline-secondary"
                  disabled={isRegistering}
                  onClick={closeRegistrationConfirmation}
                  type="button"
                >
                  Cancel
                </button>
                <button
                  className="btn btn-primary"
                  disabled={
                    !canAffordRegistration || isLoadingWallet || isRegistering
                  }
                  onClick={handleRegister}
                  type="button"
                >
                  {isRegistering ? (
                    <>
                      <span
                        aria-hidden="true"
                        className="spinner-border spinner-border-sm me-2"
                      />
                      Registering
                    </>
                  ) : (
                    "Confirm registration"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {examToRegister && <div className="modal-backdrop show" />}
    </main>
  );
}

export default AvailableExamsPage;

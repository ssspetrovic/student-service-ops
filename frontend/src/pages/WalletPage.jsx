import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  SuccessNotification,
} from "../components/PageStates";
import { formatDate } from "../utils/date";

function formatCause(cause) {
  return cause.replaceAll("_", " ");
}

function WalletPage() {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState(null);
  const [error, setError] = useState("");
  const [amount, setAmount] = useState("");
  const [depositError, setDepositError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isDepositing, setIsDepositing] = useState(false);
  const [isDepositFormValid, setIsDepositFormValid] = useState(false);

  const loadWallet = async () => {
    setError("");

    try {
      const [walletResponse, transactionResponse] = await Promise.all([
        api.get("/finance/wallet/"),
        api.get("/finance/transactions/"),
      ]);
      setWallet(walletResponse.data);
      setTransactions(transactionResponse.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to load your wallet."));
    }
  };

  useEffect(() => {
    let isCurrent = true;

    Promise.all([
      api.get("/finance/wallet/"),
      api.get("/finance/transactions/"),
    ])
      .then(([walletResponse, transactionResponse]) => {
        if (isCurrent) {
          setWallet(walletResponse.data);
          setTransactions(transactionResponse.data);
        }
      })
      .catch((requestError) => {
        if (isCurrent)
          setError(
            getErrorMessage(requestError, "Unable to load your wallet."),
          );
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const handleDeposit = async (event) => {
    event.preventDefault();
    setDepositError("");
    setSuccessMessage("");
    setIsDepositing(true);

    try {
      await api.post("/finance/deposit/", { amount });
      setAmount("");
      setIsDepositFormValid(false);
      setSuccessMessage("Funds deposited.");
      await loadWallet();
    } catch (requestError) {
      setDepositError(
        getErrorMessage(requestError, "Unable to deposit funds."),
      );
    } finally {
      setIsDepositing(false);
    }
  };

  const changeDepositAmount = (event) => {
    setAmount(event.target.value);
    setIsDepositFormValid(event.currentTarget.form.checkValidity());
  };

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My wallet</h1>
      {error && <ErrorState message={error} />}
      {depositError && <ErrorState message={depositError} />}
      {(!wallet || !transactions) && !error && (
        <LoadingState label="your wallet" />
      )}
      {wallet && transactions && (
        <>
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5">Current balance</h2>
              <p className="display-6 mb-0">{wallet.balance} RSD</p>
            </div>
          </div>
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5">Deposit funds</h2>
              <form
                className="row gy-3 align-items-end"
                onSubmit={handleDeposit}
              >
                <div className="col-sm-6 col-md-4">
                  <label className="form-label" htmlFor="deposit-amount">
                    Amount (RSD)
                  </label>
                  <input
                    className="form-control"
                    id="deposit-amount"
                    inputMode="decimal"
                    min="1.00"
                    onChange={changeDepositAmount}
                    required
                    step="0.01"
                    type="number"
                    value={amount}
                  />
                </div>
                <div className="col-sm-auto">
                  <button
                    className="btn btn-primary"
                    disabled={isDepositing || !isDepositFormValid}
                    type="submit"
                  >
                    {isDepositing ? (
                      <>
                        <span
                          aria-hidden="true"
                          className="spinner-border spinner-border-sm me-2"
                        />
                        Depositing funds
                      </>
                    ) : (
                      "Deposit funds"
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
          <h2 className="h4 mb-3">Transaction history</h2>
          {transactions.length === 0 ? (
            <EmptyState>You have no wallet transactions.</EmptyState>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped align-middle">
                <thead>
                  <tr>
                    <th className="ps-3">Date</th>
                    <th>Cause</th>
                    <th className="pe-3">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((transaction) => (
                    <tr key={transaction.id}>
                      <td className="ps-3">
                        {formatDate(transaction.created_at)}
                      </td>
                      <td className="text-capitalize">
                        {formatCause(transaction.cause)}
                      </td>
                      <td className="pe-3">{transaction.amount} RSD</td>
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
    </main>
  );
}

export default WalletPage;

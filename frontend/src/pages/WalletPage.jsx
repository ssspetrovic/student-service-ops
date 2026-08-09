import { useEffect, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../api/errorMessage";
import { EmptyState, ErrorState, LoadingState } from "../components/PageStates";

function formatDate(date) {
  return new Date(date).toLocaleString();
}

function formatCause(cause) {
  return cause.replaceAll("_", " ");
}

function WalletPage() {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState(null);
  const [error, setError] = useState("");

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

  return (
    <main className="container py-5">
      <h1 className="h2 mb-4">My wallet</h1>
      {error && <ErrorState message={error} />}
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
          <h2 className="h4 mb-3">Transaction history</h2>
          {transactions.length === 0 ? (
            <EmptyState>You have no wallet transactions.</EmptyState>
          ) : (
            <div className="table-responsive">
              <table className="table table-striped align-middle">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Cause</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((transaction) => (
                    <tr key={transaction.id}>
                      <td>{formatDate(transaction.created_at)}</td>
                      <td className="text-capitalize">
                        {formatCause(transaction.cause)}
                      </td>
                      <td>{transaction.amount} RSD</td>
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

export default WalletPage;

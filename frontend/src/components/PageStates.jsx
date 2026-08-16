import { useEffect } from "react";

export function LoadingState({ label }) {
  return (
    <div className="d-flex justify-content-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Loading {label}</span>
      </div>
    </div>
  );
}

export function ErrorState({ message }) {
  return (
    <p className="alert alert-danger" role="alert">
      {message}
    </p>
  );
}

export function EmptyState({ children }) {
  return (
    <p className="alert alert-info" role="status">
      {children}
    </p>
  );
}

export function SuccessNotification({ message, onDismiss }) {
  useEffect(() => {
    if (!message) {
      return undefined;
    }

    const timeout = window.setTimeout(onDismiss, 3000);

    return () => window.clearTimeout(timeout);
  }, [message, onDismiss]);

  if (!message) {
    return null;
  }

  return (
    <div
      className="alert alert-success alert-dismissible bottom-0 end-0 m-4 position-fixed z-3"
      role="status"
    >
      {message}
      <button
        aria-label="Close"
        className="btn-close small"
        onClick={onDismiss}
        type="button"
      />
    </div>
  );
}

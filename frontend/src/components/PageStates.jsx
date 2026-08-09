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

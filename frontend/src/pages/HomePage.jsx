import { Navigate } from "react-router-dom";
import useAuth from "../auth/useAuth";

function HomePage() {
  const { user } = useAuth();

  if (user?.role === "student") {
    return <Navigate to="/profile" replace />;
  }

  if (user?.role === "professor") {
    return <Navigate to="/professor/profile" replace />;
  }

  if (user?.role === "admin") {
    return <Navigate to="/admin" replace />;
  }

  return <Navigate to="/login" replace />;
}

export default HomePage;

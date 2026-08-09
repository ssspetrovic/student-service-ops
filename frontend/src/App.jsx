import { Navigate, Route, Routes } from "react-router-dom";
import AppNavbar from "./components/AppNavbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AvailableExamsPage from "./pages/AvailableExamsPage";
import CurriculumPage from "./pages/CurriculumPage";
import EnrollmentsPage from "./pages/EnrollmentsPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import RegistrationsPage from "./pages/RegistrationsPage";
import ResultsPage from "./pages/ResultsPage";
import StudentProfilePage from "./pages/StudentProfilePage";
import WalletPage from "./pages/WalletPage";

function App() {
  return (
    <>
      <AppNavbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/student" element={<Navigate to="/profile" replace />} />
        <Route
          path="/profile"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <StudentProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/exams/available"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <AvailableExamsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/curriculum"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <CurriculumPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/enrollments"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <EnrollmentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/registrations"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <RegistrationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/results"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <ResultsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wallet"
          element={
            <ProtectedRoute allowedRoles={["student"]}>
              <WalletPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}

export default App;

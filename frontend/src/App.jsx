import { Navigate, Route, Routes } from "react-router-dom";
import AppNavbar from "./components/AppNavbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AvailableExamsPage from "./pages/AvailableExamsPage";
import AdminCoursesPage from "./pages/AdminCoursesPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import AdminProgramsPage from "./pages/AdminProgramsPage";
import AdminUserFormPage from "./pages/AdminUserFormPage";
import AdminUsersPage from "./pages/AdminUsersPage";
import CurriculumPage from "./pages/CurriculumPage";
import EnrollmentsPage from "./pages/EnrollmentsPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import RegistrationsPage from "./pages/RegistrationsPage";
import ResultsPage from "./pages/ResultsPage";
import ProfessorExamCreatePage from "./pages/ProfessorExamCreatePage";
import ProfessorExamListPage from "./pages/ProfessorExamListPage";
import ProfessorExamRegistrationsPage from "./pages/ProfessorExamRegistrationsPage";
import ProfessorProfilePage from "./pages/ProfessorProfilePage";
import StudentProfilePage from "./pages/StudentProfilePage";
import StudentRegistrationPage from "./pages/StudentRegistrationPage";
import WalletPage from "./pages/WalletPage";

function App() {
  return (
    <>
      <AppNavbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<StudentRegistrationPage />} />
        <Route path="/student" element={<Navigate to="/profile" replace />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users/new"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminUserFormPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users/:id/edit"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminUserFormPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/programs"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminProgramsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/courses"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminCoursesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/professor"
          element={<Navigate to="/professor/profile" replace />}
        />
        <Route
          path="/professor/profile"
          element={
            <ProtectedRoute allowedRoles={["professor"]}>
              <ProfessorProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/professor/exams"
          element={
            <ProtectedRoute allowedRoles={["professor"]}>
              <ProfessorExamListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/professor/exams/new"
          element={
            <ProtectedRoute allowedRoles={["professor"]}>
              <ProfessorExamCreatePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/professor/exams/:examId/registrations"
          element={
            <ProtectedRoute allowedRoles={["professor"]}>
              <ProfessorExamRegistrationsPage />
            </ProtectedRoute>
          }
        />
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

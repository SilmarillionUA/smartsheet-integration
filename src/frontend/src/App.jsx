import React from "react";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Sheets from "./pages/Sheets";
import Checklist from "./pages/Checklist";

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login/" />;
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  return isAuthenticated ? <Navigate to="/sheets/" /> : children;
}

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light border-bottom mb-4">
      <div className="container">
        <Link className="navbar-brand" to="/">
          Checklist App
        </Link>

        {isAuthenticated && (
          <div>
            <span className="me-3">{user?.name}</span>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={logout}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          <Route
            path="/login/"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />
          <Route
            path="/register/"
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            }
          />
          <Route
            path="/sheets/"
            element={
              <PrivateRoute>
                <Sheets />
              </PrivateRoute>
            }
          />
          <Route
            path="/sheets/:sheetId/"
            element={
              <PrivateRoute>
                <Checklist />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/sheets/" />} />
        </Routes>
      </div>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

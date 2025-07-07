import React from 'react';
import { Routes, Route,useLocation } from "react-router-dom";
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from "./pages/Home";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";
import Dashboard from './pages/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import InterviewRoom from './pages/InterviewRoom';

function App() {
  const location = useLocation();
  return (
      <AuthProvider>
        {!location.pathname.includes('/interview') && <Navbar />}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/interview/:sessionId"
            element={
              <PrivateRoute>
                <InterviewRoom />
              </PrivateRoute>
            }
          />
        </Routes>
      </AuthProvider>
  );
}

export default App;

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { currentUser } = useAuth();

  return (
    <nav className="p-4 shadow bg-white">
      <div className="max-w-7xl mx-auto flex justify-between items-center">

      <Link to="/">
      <h1 className="text-2xl font-bold text-blue-600">InterviewAI</h1>
      </Link>

      <div className="flex gap-4">
        {!currentUser && (
          <>
          <div className="space-x-4">
            <Link to="/signin">
            <button className="text-gray-700 hover:text-blue-600 font-medium transition">
              Sign In
            </button>
           </Link>
            <Link to="/signup">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition">
              Sign Up
            </button>
          </Link>
          </div>
          </>
        )}
        {currentUser && (
          <>
            <Link to="/dashboard" className="hover:underline">Dashboard</Link>
          </>
        )}
       </div>
       </div>
    </nav>
  );
};

export default Navbar;


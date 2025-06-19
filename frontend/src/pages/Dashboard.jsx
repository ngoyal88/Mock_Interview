import React from 'react';
import { useAuth } from '../context/AuthContext';
import ResumeUpload from '../components/ResumeUpload';
import { useState } from 'react';
import useUserProfile from "../hooks/useUserProfile";

const Dashboard = () => {
  const { currentUser, logout } = useAuth();
  const [parsedResume, setParsedResume] = useState(null);
  const { profile, loading } = useUserProfile();

  if (loading) return <p>Loading your profile...</p>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">👋 Welcome, {profile.name}</h1>
          <p className="text-sm text-gray-500">UID: {currentUser?.uid}</p>
        </div>
        <button
          onClick={logout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Resume Upload Section */}
      <ResumeUpload onParsed={setParsedResume} />

      {/* Parsed Resume Summary */}
      {parsedResume && (
        <div className="bg-white shadow rounded-lg p-4 mt-6">
          <h2 className="text-xl font-semibold mb-2">🧠 Resume Summary</h2>
          <p><strong>Name:</strong> {parsedResume.name || "N/A"}</p>
          <p><strong>Email:</strong> {parsedResume.email || "N/A"}</p>
          <p><strong>Phone:</strong> {parsedResume.phone || "N/A"}</p>
          <p><strong>Skills:</strong> {(parsedResume.skills || []).join(', ')}</p>
          <p><strong>Education:</strong> {(parsedResume.education || []).join(', ')}</p>
          <p><strong>Experience:</strong> {(parsedResume.experience || []).join(', ')}</p>
        </div>
      )}

      {/* Interview Section */}
      <div className="bg-white shadow rounded-lg p-4 mt-6">
        <h2 className="text-xl font-semibold mb-2">🎤 Start Mock Interview</h2>
        <button
          className={`px-4 py-2 rounded text-white ${
            parsedResume
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
          disabled={!parsedResume}
          onClick={() => {
            // Later: start interview API call
            alert('Interview feature coming soon!');
          }}
        >
          Start Interview
        </button>
      </div>

      {/* Placeholder for Interview History */}
      <div className="bg-white shadow rounded-lg p-4 mt-6">
        <h2 className="text-xl font-semibold mb-2">📚 Interview History</h2>
        <p className="text-gray-500">Coming soon: See your past interviews, scores, and feedback.</p>
      </div>
    </div>
  );
};

export default Dashboard;
import React, { useState } from "react";
import useUserProfile from "../hooks/useUserProfile";
import { useParams } from 'react-router-dom';

const InterviewRoom = () => {
  const { sessionId } = useParams();
  console.log("Interview session ID:", sessionId);
  const { profile, loading } = useUserProfile();
  const [chatLog, setChatLog] = useState([
    { from: "ai", text: "Hello! Let's begin your SDE-1 mock interview. Can you introduce yourself?" },
  ]);
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (!message.trim()) return;

    const updatedLog = [...chatLog, { from: "user", text: message }];
    setChatLog(updatedLog);
    setMessage("");

    // 👉 Later: send message to backend and get AI response
    setTimeout(() => {
      setChatLog([...updatedLog, { from: "ai", text: "Thanks! Tell me about your favorite project." }]);
    }, 1000);
  };

  if (loading) return <div className="p-6">Loading your profile...</div>;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="p-4 bg-white shadow flex justify-between items-center">
        <h1 className="text-xl font-bold">AI Interview Room</h1>
        <p className="text-sm text-gray-600">Interviewing: {profile.name}</p>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left: AI Avatar */}
        <div className="w-1/3 p-4 border-r bg-white">
          <h2 className="text-lg font-semibold mb-2">🎥 Interviewer</h2>
          <div className="aspect-video w-full bg-gray-200 flex items-center justify-center rounded shadow-inner">
            {/* Later: Embed D-ID here */}
            <p className="text-gray-500">[Avatar Here]</p>
          </div>
        </div>

        {/* Center: Chat */}
        <div className="w-1/3 p-4 overflow-y-auto flex flex-col border-r">
          <h2 className="text-lg font-semibold mb-2">💬 Chat</h2>
          <div className="flex-1 space-y-2 overflow-y-auto">
            {chatLog.map((msg, i) => (
              <div key={i} className={`p-2 rounded ${msg.from === "ai" ? "bg-blue-100 text-left" : "bg-green-100 text-right"}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <div className="mt-4 flex">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 border px-3 py-2 rounded-l"
              placeholder="Type your answer..."
            />
            <button onClick={handleSend} className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700">
              Send
            </button>
          </div>
        </div>

        {/* Right: Code Editor Placeholder */}
        <div className="w-1/3 p-4 bg-white">
          <h2 className="text-lg font-semibold mb-2">👨‍💻 Code Editor</h2>
          <div className="h-full bg-gray-100 p-2 rounded shadow-inner">
            {/* Monaco editor will be added here */}
            <p className="text-gray-500 text-sm">Code editor coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewRoom;

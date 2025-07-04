import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import useUserProfile from "../hooks/useUserProfile";
import useInterviewFlow from "../components/useInterviewFlow";
import AvatarDisplay from "../components/AvatarDisplay";
import MicInput from "../components/MicInput";
import CodeEditor from "../components/CodeEditor";
import ChatDrawer from "../components/ChatDrawer";
import { getRandomDSAQuestion } from "../utils/getRandomDSAQuestion";
import DSAQuestionDisplay from "../components/DSAQuestionDisplay";

const InterviewRoom = () => {
  const { sessionId } = useParams();
  console.log(sessionId);
  const { profile, ploading } = useUserProfile();

  const {
    startInterview,
    isSpeaking,
    isListening,
    chatLog,
    question,
    currentPhase, // "behavioral" | "theory" | "dsa"
  } = useInterviewFlow({ profile });

  const [showChat, setShowChat] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  useEffect(() => {
  const q = getRandomDSAQuestion("hard");
  setCurrentQuestion(q);
}, []);

  useEffect(() => {
    if (profile) startInterview();
  }, [profile, startInterview]);

  if (ploading || !profile) return <div className="p-6">Loading your profile...</div>;

  return (
    <div className="h-screen flex flex-col bg-[#0e0e10] text-white">
      {/* Header */}
      <header className="p-4 bg-[#1c1c1e] shadow flex justify-between items-center border-b border-gray-700">
        <h1 className="text-xl font-bold text-cyan-400">🧠 AI Interview Room</h1>
        <div className="flex items-center gap-4">
          <p className="text-sm text-gray-400">Interviewing: {profile.name}</p>
          <button
            onClick={() => setShowChat(!showChat)}
            className="text-sm px-3 py-1 border border-cyan-500 rounded hover:bg-cyan-500 hover:text-black transition"
          >
            {showChat ? "Hide Chat" : "Show Chat"}
          </button>
        </div>
      </header>

      {/* Main Layout */}
      {currentPhase === "dsa" ? (
        // 💬 Fullscreen Avatar with optional Chat
        <div className="flex flex-1 transition-all duration-500">
          <div className="flex-1 p-4 bg-black flex justify-center items-center">
            <AvatarDisplay loading={isSpeaking} />
          </div>

          {showChat && (
            <div className="w-1/3 bg-[#1c1c1e] p-4 border-l border-gray-700 overflow-y-auto">
              <ChatDrawer chatLog={chatLog} />
            </div>
          )}
        </div>
      ) : (
        // 👨‍💻 DSA Mode Layout
        <div className="flex flex-1 transition-all duration-500 overflow-hidden">
          {/* Left: Avatar + Chat stacked */}
          <div className="w-1/3 flex flex-col border-r border-gray-800 bg-[#141417]">
            <div className="p-4 h-1/2">
              <AvatarDisplay loading={isSpeaking} />
            </div>
            <div className="h-1/2 p-4 overflow-y-auto border-t border-gray-800">
              <ChatDrawer chatLog={chatLog} />
            </div>
          </div>

          {/* Center: DSA Question */}
          <div className="w-1/3 p-4 overflow-y-auto bg-[#0f0f11] border-r border-gray-800">
            <DSAQuestionDisplay question={currentQuestion} />
          </div>

          {/* Right: Code Editor */}
          <div className="w-1/3 p-4 bg-[#0a0a0c]">
            <CodeEditor question={question} />
          </div>
        </div>
      )}

      {/* Mic Feedback */}
      <MicInput isListening={isListening} isSpeaking={isSpeaking} />
    </div>
  );
};

export default InterviewRoom;

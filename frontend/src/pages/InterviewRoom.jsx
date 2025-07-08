import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useUserProfile from "../hooks/useUserProfile";
import useInterviewFlow from "../components/useInterviewFlow";
import AvatarDisplay from "../components/AvatarDisplay";
import MicInput from "../components/MicInput";
import CodeEditor from "../components/CodeEditor";
import ChatDrawer from "../components/ChatDrawer";
import { getRandomDSAQuestion } from "../utils/getRandomDSAQuestion";
import DSAQuestionDisplay from "../components/DSAQuestionDisplay";
import CandidateWebcam from "../components/CandidateWebcam";

const InterviewRoom = () => {
  const { sessionId } = useParams();
  console.log(sessionId);
  const navigate = useNavigate();
  const { profile, ploading } = useUserProfile();

  const {
    startInterview,
    isSpeaking,
    isListening,
    question,
    currentPhase, // "behavioral" | "theory" | "dsa"
  } = useInterviewFlow({ profile });

  const [showChat, setShowChat] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  const [chatLog, setChatLog] = useState([
  { from: "ai", text: "Hello! Let's begin your interview. Feel free to chat with me here anytime." },
]);

  useEffect(() => {
  const q = getRandomDSAQuestion("hard");
  setCurrentQuestion(q);
  }, []);

  useEffect(() => {
    if (profile) startInterview();
  }, [profile, startInterview]);

  if (ploading || !profile) return <div className="p-6">Loading your profile...</div>;

  const endInterview = () => {
    if (window.confirm("Are you sure you want to end the interview?")) {
      navigate("/dashboard");
    }
  };

  return (
    
    <div className="h-screen overflow-hidden flex flex-col bg-[#0e0e10] text-white">
      <header className="p-4 bg-[#1c1c1e] shadow flex justify-between items-center border-b border-gray-700">
        <h1 className="text-xl font-bold text-cyan-400">🧠 AI Interview Room</h1>
        <div className="flex items-center gap-4">
          <p className="text-sm text-gray-400">Interviewing: {profile.name}</p>
          {currentPhase !== "dsa" && (
            <button
              onClick={() => setShowChat(!showChat)}
              className="text-sm px-3 py-1 border border-cyan-500 rounded hover:bg-cyan-500 hover:text-black transition"
            >
              {showChat ? "Hide Chat" : "Show Chat"}
            </button>
          )}

          <button
            onClick={endInterview}
            className="text-sm px-3 py-1 border border-red-500 text-red-500 rounded hover:bg-red-600 hover:text-white transition"
          >
            End Interview
          </button>
        </div>
      </header>

      {/* Main Layout */}
      {currentPhase !== "dsa" ? (
        // 💬 Fullscreen Avatar with optional Chat
        <div className="flex flex-1 h-[calc(100vh-80px)] overflow-hidden">
          <div className="flex-1 relative bg-black flex justify-center items-center h-full transition-all duration-500">
            <AvatarDisplay loading={isSpeaking} />
            
            <div className="absolute bottom-6 right-6 w-96 h-60 z-20 border border-gray-800 rounded-md overflow-hidden shadow-md bg-black">
              <CandidateWebcam />
            </div>
          </div>

          {showChat && (
            <div className="w-[25%] p-4 border-l border-gray-800 bg-[#1c1c1e] overflow-y-auto">
               <ChatDrawer
                 chatLog={chatLog}
                 onSend={(msg) => {
                   setChatLog((prev) => [...prev, { from: "user", text: msg }]);
                   setTimeout(() => {
                     setChatLog((prev) => [...prev, { from: "ai", text: "Thanks for your message!" }]);
                   }, 1000);
                 }}
               />
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
              {/* <ChatDrawer
                chatLog={chatLog}
                onSend={(msg) => {
                  setChatLog((prev) => [...prev, { from: "user", text: msg }]);
                  setTimeout(() => {
                    setChatLog((prev) => [...prev, { from: "ai", text: "Thanks for your message!" }]);
                  }, 1000);
                }}
              /> */}
              <CandidateWebcam />
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

import React, { useState } from "react";
import { Send } from "lucide-react";


const ChatDrawer = ({ chatLog = [], onSend }) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (!message.trim()) return;
    onSend?.(message.trim());
    setMessage("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
        {chatLog.map((msg, i) => (
          <div
            key={i}
            className={`p-2 rounded text-sm max-w-[80%] ${
              msg.from === "ai"
                ? "bg-blue-800 text-left self-start"
                : "bg-green-700 text-right self-end"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            className="flex-1 p-1 rounded-1 bg-gray-800 text-white border border-gray-700 focus:outline-none"
          />
          <button
            onClick={handleSend}
            className="p-2 bg-cyan-500 text-black rounded hover:bg-cyan-400 transition"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatDrawer;

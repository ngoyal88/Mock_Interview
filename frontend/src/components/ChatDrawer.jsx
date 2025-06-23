import React from "react";

const ChatDrawer = ({ chatLog }) => {
  return (
    <div className="bg-white w-1/3 p-4 overflow-y-auto flex flex-col border-r">
      <h2 className="text-lg font-semibold mb-2">💬 Chat</h2>
      <div className="flex-1 space-y-2 overflow-y-auto">
        {chatLog.map((msg, i) => (
          <div key={i} className={`p-2 rounded ${msg.from === "ai" ? "bg-blue-100 text-left" : "bg-green-100 text-right"}`}>
            {msg.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatDrawer;

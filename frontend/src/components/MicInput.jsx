import React from "react";

const MicInput = ({ isListening, isSpeaking }) => {
  return (
    <div className="mt-4 text-center">
      {isSpeaking && <p>AI is speaking...</p>}
      {isListening && <p>Listening...</p>}
      {!isSpeaking && !isListening && <p>Waiting for your response...</p>}
    </div>
  );
};

export default MicInput;

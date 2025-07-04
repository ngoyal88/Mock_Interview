import React, { useState } from "react";

const DSAQuestionDisplay = ({ question }) => {
  const [showHints, setShowHints] = useState(false);

  if (!question) return <p className="text-gray-400">No question selected.</p>;

  return (
    <div className="bg-[#1e1e1e] text-gray-200 p-6 rounded-lg shadow-md border border-gray-700 mb-4 overflow-y-auto max-h-[60vh]">
      {/* Title & Difficulty */}
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-2xl font-bold text-yellow-400">{question.title}</h2>
        <span
          className={`text-sm px-2 py-1 rounded-full ${
            question.difficulty === "easy"
              ? "bg-green-700 text-green-300"
              : question.difficulty === "medium"
              ? "bg-yellow-700 text-yellow-300"
              : "bg-red-700 text-red-300"
          }`}
        >
          {(question.difficulty || "unknown").toUpperCase()}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 mb-4 whitespace-pre-line">{question.description}</p>

      {/* Examples */}
      {question.examples && question.examples.length > 0 && (
        <div className="mb-4">
          <h3 className="text-md font-semibold text-blue-300 mb-2">📘 Examples</h3>
          <div className="space-y-3 text-sm text-gray-300">
            {question.examples.map((ex, i) => (
              <div key={i} className="bg-[#2a2a2a] p-3 rounded border border-gray-600">
                <p><span className="text-gray-400">Input:</span> {ex.input}</p>
                <p><span className="text-gray-400">Output:</span> {ex.output}</p>
                {ex.explanation && <p><span className="text-gray-400">Explanation:</span> {ex.explanation}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Constraints */}
      {question.constraints && (
        <div className="mb-4">
          <h3 className="text-md font-semibold text-blue-300 mb-2">📏 Constraints</h3>
          <ul className="list-disc list-inside text-sm text-gray-300">
            {question.constraints.map((c, idx) => (
              <li key={idx}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Complexity */}
      {question.complexity && (
        <div className="mb-4">
          <h3 className="text-md font-semibold text-blue-300 mb-1">🧠 Expected Complexity</h3>
          <p className="text-sm text-gray-300">
            Time: {question.complexity.time} | Space: {question.complexity.space}
          </p>
        </div>
      )}

      {/* Hints Toggle */}
      {question.hints && question.hints.length > 0 && (
        <div className="mt-4">
          <button
            onClick={() => setShowHints(!showHints)}
            className="text-sm text-blue-400 hover:underline focus:outline-none"
          >
            {showHints ? "Hide Hints" : "Show Hints"}
          </button>
          {showHints && (
            <ul className="mt-2 list-disc list-inside text-sm text-yellow-300 space-y-1">
              {question.hints.map((hint, i) => (
                <li key={i}>{hint}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default DSAQuestionDisplay;

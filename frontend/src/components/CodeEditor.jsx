import React, { useState } from "react";
import Editor from "@monaco-editor/react";
import { useAuth } from "../context/AuthContext";

// 🔧 Language mapping (Judge0 language_id)
const languageMap = {
  python: 71,
  javascript: 63,
  cpp: 54,
  c: 50,
  java: 62,
  go: 60,
};

// 💻 Default starter code per language
const defaultCode = {
  python: "print('Hello, World!')",
  javascript: "console.log('Hello, World!');",
  cpp: "#include <iostream>\nint main() { std::cout << \"Hello, World!\"; return 0; }",
  c: "#include <stdio.h>\nint main() { printf(\"Hello, World!\\n\"); return 0; }",
  java: "public class Main { public static void main(String[] args) { System.out.println(\"Hello, World!\"); } }",
  go: "package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"Hello, World!\") }",
};

const CodeEditor = ({ question }) => {
  const { currentUser } = useAuth();
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(defaultCode["python"]);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const runCode = async (save = false) => {
    setLoading(true);
    setOutput("");

    try {
      const response = await fetch("http://localhost:8000/run_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language_id: languageMap[language],
          source_code: code,
          stdin: "",
          expected_output: "",
          userId: save ? currentUser?.uid : null,
          question: question || "Untitled",
        }),
      });

      const data = await response.json();
      const status = data?.status?.description || "Unknown";
      const result = data.stdout || data.stderr || data.output || "⚠️ No output";

      setOutput(`${status}\n\n${result}`);
    } catch (err) {
      setOutput(`❌ Error: ${err.message}`);
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="mb-2 flex justify-between items-center">
        {/* Language selector */}
        <div className="flex gap-3">
          <label htmlFor="language" className="font-medium text-sm">Language:</label>
          <select
            id="language"
            value={language}
            onChange={(e) => {
              setLanguage(e.target.value);
              setCode(defaultCode[e.target.value]);
            }}
            className="border px-2 py-1 rounded"
          >
            {Object.keys(languageMap).map((lang) => (
              <option key={lang} value={lang}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Run / Submit buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => runCode(false)}
            className="bg-yellow-500 text-white px-4 py-1 rounded hover:bg-yellow-600"
          >
            Run
          </button>
          <button
            onClick={() => runCode(true)}
            className="bg-green-600 text-white px-4 py-1 rounded hover:bg-green-700"
          >
            Submit
          </button>
        </div>
      </div>

      {/* Code editor */}
      <div className="flex-1 border rounded overflow-hidden shadow">
        <Editor
          height="100%"
          language={language}
          value={code}
          onChange={(value) => setCode(value)}
          theme="vs-dark"
          options={{
            fontSize: 14,
            minimap: { enabled: false },
            automaticLayout: true,
          }}
        />
      </div>

      {/* Output display */}
      <div className="mt-3">
        <h3 className="text-sm font-medium mb-1">Output:</h3>
        <div className="bg-gray-100 text-sm font-mono p-2 rounded border h-36 overflow-auto">
          {loading ? "⏳ Running..." : output || "No output yet."}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;

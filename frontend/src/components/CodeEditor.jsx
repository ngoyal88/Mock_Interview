// src/components/CodeEditor.jsx
import React, { useState } from "react";
import Editor from "@monaco-editor/react";

// Supported languages and sample templates
const languageTemplates = {
  javascript: `function hello() {\n  console.log("Hello, world!");\n}`,
  typescript: `function hello(): void {\n  console.log("Hello, world!");\n}`,
  python: `def hello():\n    print("Hello, world!")`,
  cpp: `#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, world!" << endl;\n    return 0;\n}`,
  c: `#include <stdio.h>\n\nint main() {\n    printf("Hello, world!\\n");\n    return 0;\n}`,
  java: `public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, world!");\n    }\n}`,
  go: `package main\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, world!")\n}`,
};


const CodeEditor = () => {
  const [language, setLanguage] = useState("javascript");
  const [code, setCode] = useState(languageTemplates["javascript"]);
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    setCode(languageTemplates[newLang]);
    setOutput("");
  };

  const runCode = async () => {
    setIsRunning(true);
    setOutput("Running...");

    try {
      const res = await fetch("http://localhost:8000/run_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, code }),
      });

      const data = await res.json();
      setOutput(data.output || "No output received");
    } catch (err) {
      setOutput("❌ Error running code");
      console.error(err);
    }

    setIsRunning(false);
  };

  return (
    <div className="h-full flex flex-col space-y-2">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <div className="space-x-2">
          <label className="font-medium">Language:</label>
          <select
          className="border px-2 py-1 rounded"
          value={language}
          onChange={handleLanguageChange}
          >
            {Object.keys(languageTemplates).map((lang) => (
                <option key={lang} value={lang}>
                    {lang.charAt(0).toUpperCase() + lang.slice(1)}
                </option>
            ))}
            </select>
        </div>

        <button
          onClick={runCode}
          disabled={isRunning}
          className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700 transition"
        >
          {isRunning ? "Running..." : "Run Code"}
        </button>
      </div>

      {/* Code Editor */}
      <div className="flex-1 border rounded overflow-hidden shadow-inner">
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

      {/* Output Panel */}
      <div className="mt-2 border rounded bg-black text-green-400 p-2 text-sm h-24 overflow-y-auto">
        <pre>{output}</pre>
      </div>
    </div>
  );
};

export default CodeEditor;

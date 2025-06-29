import React, { useState } from "react";
import Editor from "@monaco-editor/react";

const templates = {
  python: `def hello():\n    print("Hello, world!")`,
  javascript: `function hello() {\n  console.log("Hello, world!");\n}`,
  cpp: `#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello, world!";\n    return 0;\n}`,
  c: `#include <stdio.h>\nint main() {\n    printf("Hello, world!\\n");\n    return 0;\n}`,
  java: `public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, world!");\n    }\n}`,
  go: `package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello, world!")\n}`,
};

const CodeEditor = ({ question = "Reverse a linked list", userId }) => {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(templates["python"]);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const runCode = async (save = false) => {
    setLoading(true);
    setOutput("Running...");

    const res = await fetch("http://localhost:8000/run_code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        language,
        code,
        question,
        userId: save ? userId : null,
      }),
    });

    const data = await res.json();
    setOutput(data.output || "No output");
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-full p-4 space-y-4 bg-white rounded shadow">
      <div className="flex justify-between items-center">
        <div>
          <label className="mr-2 font-medium">Language:</label>
          <select
            className="border rounded px-2 py-1"
            value={language}
            onChange={(e) => {
              setLanguage(e.target.value);
              setCode(templates[e.target.value]);
              setOutput("");
            }}
          >
            {Object.keys(templates).map((lang) => (
              <option key={lang}>{lang}</option>
            ))}
          </select>
        </div>
        <div className="space-x-2">
          <button
            onClick={() => runCode(false)}
            className="bg-gray-600 text-white px-4 py-1 rounded"
          >
            Run
          </button>
          <button
            onClick={() => runCode(true)}
            className="bg-blue-600 text-white px-4 py-1 rounded"
          >
            Submit
          </button>
        </div>
      </div>

      <Editor
        height="50vh"
        language={language}
        value={code}
        onChange={(val) => setCode(val)}
        theme="vs-dark"
        options={{ fontSize: 14, minimap: { enabled: false } }}
      />

      <div className="bg-black text-green-400 p-3 rounded text-sm h-28 overflow-y-auto">
        <pre>{loading ? "⏳ Running..." : output}</pre>
      </div>
    </div>
  );
};

export default CodeEditor;

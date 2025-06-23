import { useEffect, useRef, useState, useCallback } from "react";

const useInterviewFlow = ({ profile, resume }) => {
  const recognitionRef = useRef(null);
  const [question, setQuestion] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [transcript, setTranscript] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // 🎙 Start mic
  const startListening = useCallback(() => {
    if (recognitionRef.current) {
      setTranscript("");
      setIsListening(true);
      recognitionRef.current.start();
    }
  }, []);

  // 🔊 Speak and then listen
  const speakThenListen = useCallback(
    (text) => {
      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = 1;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        startListening();
      };

      synth.speak(utterance);
    },
    [startListening] // ✅ Added dependency here
  );

  // 🔁 Handle follow-up
  const handleFollowUp = useCallback(
    async (userAnswer) => {
      const updatedLog = [...chatLog, { from: "user", text: userAnswer }];

      const res = await fetch("http://localhost:8000/interview/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: profile?.name || "Candidate",
          resume,
          role: "SDE-1",
          last_question: question,
          user_answer: userAnswer,
          question_history: updatedLog
            .filter((msg) => msg.from === "ai")
            .map((msg) => msg.text)
            .join("\n"),
        }),
      });

      const data = await res.json();
      const nextQ = data.follow_up_question;

      setQuestion(nextQ);
      setChatLog([...updatedLog, { from: "ai", text: nextQ }]);
      speakThenListen(nextQ);
    },
    [chatLog, profile, resume, question, speakThenListen]
  );

  // 🎤 Setup mic once
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
      handleFollowUp(text);
    };

    recognition.onerror = (e) => {
      console.error("Mic error:", e);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
  }, [handleFollowUp]);

  // 🚀 Start interview
  const startInterview = useCallback(async () => {
    const res = await fetch("http://localhost:8000/start_interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: profile?.name || "Candidate",
        resume,
        role: "SDE-1",
      }),
    });

    const data = await res.json();
    setQuestion(data.question);
    setChatLog([{ from: "ai", text: data.question }]);
    speakThenListen(data.question);
  }, [profile, resume, speakThenListen]);

  return {
    startInterview,
    isSpeaking,
    isListening,
    question,
    chatLog,
    transcript,
  };
};

export default useInterviewFlow;

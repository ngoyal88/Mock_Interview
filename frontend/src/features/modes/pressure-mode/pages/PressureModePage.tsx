import ComingSoonModePage from "features/modes/shared/components/ComingSoonModePage";

const FEATURES = [
  "Minimal hints, fast follow-ups",
  "Interrupt-driven questioning style",
  "Focus on clarity, speed, and confidence",
  "Simulates real interviewer pressure dynamics",
] as const;

export default function PressureModePage() {
  return (
    <ComingSoonModePage
      modeLabel="Pressure"
      description="This mode simulates high-pressure interview environments where hesitation, incomplete answers, and weak reasoning are challenged immediately. The AI becomes stricter, faster, and less forgiving—closer to real hiring loops."
      features={FEATURES}
      footerNote="Work in progress · designed for high-intensity practice"
    />
  );
}

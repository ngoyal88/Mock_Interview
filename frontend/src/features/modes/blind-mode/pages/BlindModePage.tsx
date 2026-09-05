import ComingSoonModePage from "features/modes/shared/components/ComingSoonModePage";

const FEATURES = [
  "No hints, no scaffolding, no framing",
  "Emphasis on first-principles thinking",
  "Tests problem interpretation under uncertainty",
  "Closest to cold-start interview scenarios",
] as const;

export default function BlindModePage() {
  return (
    <ComingSoonModePage
      modeLabel="Blind"
      description="In Blind Mode, context is stripped away. No hints about the topic, difficulty, or expected direction. You respond with pure reasoning—just like in real interviews where the problem is unfamiliar and clarity must come from you."
      features={FEATURES}
      footerNote="Work in progress · built for raw reasoning evaluation"
    />
  );
}

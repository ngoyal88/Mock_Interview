import React from 'react';
import { MicOff, SlidersHorizontal } from 'lucide-react';

import { ProfileSection } from './ProfileSection';
import { ProfileSwitchField } from '../shared/ProfileSwitchField';

type InterviewBehaviorSectionProps = {
  skipPrecheck: boolean;
  onSkipPrecheckChange: (value: boolean) => void;
};

export function InterviewBehaviorSection({
  skipPrecheck,
  onSkipPrecheckChange,
}: InterviewBehaviorSectionProps) {
  return (
    <ProfileSection
      icon={SlidersHorizontal}
      title="Interview behavior"
      description="How sessions launch on your device."
    >
      <ProfileSwitchField
        id="profile-skip-precheck"
        label="Skip device check"
        description="Join interviews immediately without the pre-session mic and connection check."
        checked={skipPrecheck}
        onChange={onSkipPrecheckChange}
      />
      <p className="profile-field__hint profile-field__hint--inline">
        <MicOff className="inline h-4 w-4 align-text-bottom" aria-hidden /> Applies to your browser only — not synced across devices.
      </p>
    </ProfileSection>
  );
}

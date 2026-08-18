import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

import { ProfileSection } from './ProfileSection';

export function PlanSection() {
  return (
    <ProfileSection
      icon={Sparkles}
      title="Plan"
      description="Your workspace tier and upgrade options."
    >
      <div className="profile-plan-panel">
        <p className="profile-plan-panel__tier">Free</p>
        <p className="profile-plan-panel__copy">
          Core mock interviews, vault storage, and session history.
        </p>
        <Link to="/pricing" className="profile-btn profile-btn--primary">
          Upgrade to Pro
        </Link>
      </div>
    </ProfileSection>
  );
}

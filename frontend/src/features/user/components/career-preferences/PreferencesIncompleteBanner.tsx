import React from 'react';
import { AlertCircle, Sparkles } from 'lucide-react';

type PreferencesIncompleteBannerProps = {
  message: string;
};

export function PreferencesIncompleteBanner({ message }: PreferencesIncompleteBannerProps) {
  return (
    <div className="profile-prefs-banner" role="status">
      <div className="profile-prefs-banner__icon-wrap" aria-hidden>
        <AlertCircle className="profile-prefs-banner__icon" />
      </div>
      <div className="min-w-0">
        <p className="profile-prefs-banner__title">Preferences incomplete</p>
        <p className="profile-prefs-banner__text">{message}</p>
      </div>
      <Sparkles className="profile-prefs-banner__spark hidden sm:block" aria-hidden />
    </div>
  );
}

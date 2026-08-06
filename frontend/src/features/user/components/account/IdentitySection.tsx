import React, { useState } from 'react';
import { BadgeCheck, Mail, UserRound } from 'lucide-react';
import type { User } from 'firebase/auth';

import { hasPasswordProvider, signInMethodLabel, userInitials } from '../../utils/accountSettingsUtils';
import { ProfileSection } from './ProfileSection';

type IdentitySectionProps = {
  user: User;
  displayName: string;
  photoUrl: string;
  saving: boolean;
  sendingVerification: boolean;
  sendingReset: boolean;
  onDisplayNameChange: (value: string) => void;
  onPhotoUrlChange: (value: string) => void;
  onSave: () => void;
  onSendVerification: () => void;
  onResetPassword: () => void;
};

export function IdentitySection({
  user,
  displayName,
  photoUrl,
  saving,
  sendingVerification,
  sendingReset,
  onDisplayNameChange,
  onPhotoUrlChange,
  onSave,
  onSendVerification,
  onResetPassword,
}: IdentitySectionProps) {
  const [photoFailed, setPhotoFailed] = useState(false);
  const previewUrl = photoUrl.trim() && !photoFailed ? photoUrl.trim() : null;
  const initials = userInitials(user, displayName);
  const showVerification = Boolean(user.email) && !user.emailVerified;
  const showReset = hasPasswordProvider(user);

  return (
    <ProfileSection
      icon={UserRound}
      title="Identity"
      description="How you appear in interviews and across Vetta."
    >
      <div className="profile-identity__avatar-row">
        <div className="profile-identity__avatar" aria-hidden>
          {previewUrl ? (
            <img
              src={previewUrl}
              alt=""
              className="h-full w-full object-cover"
              referrerPolicy="no-referrer"
              onError={() => setPhotoFailed(true)}
            />
          ) : (
            <span>{initials}</span>
          )}
        </div>
        <div className="profile-identity__badges">
          <span
            className={`profile-badge ${user.emailVerified ? 'profile-badge--verified' : 'profile-badge--unverified'}`}
          >
            {user.emailVerified ? 'Email verified' : 'Email not verified'}
          </span>
          <span className="profile-badge profile-badge--provider">{signInMethodLabel(user)}</span>
        </div>
      </div>

      <div className="profile-field-grid">
        <label className="profile-field">
          <span className="profile-field__label">Email</span>
          <div className="profile-input-wrap profile-input-wrap--readonly">
            <Mail className="profile-input-wrap__icon" aria-hidden />
            <input type="email" value={user.email || ''} readOnly className="profile-input" />
          </div>
        </label>

        <label className="profile-field">
          <span className="profile-field__label">Display name</span>
          <div className="profile-input-wrap">
            <BadgeCheck className="profile-input-wrap__icon" aria-hidden />
            <input
              type="text"
              value={displayName}
              onChange={(e) => onDisplayNameChange(e.target.value)}
              className="profile-input"
              placeholder="Your name"
              autoComplete="name"
            />
          </div>
        </label>
      </div>

      <label className="profile-field">
        <span className="profile-field__label">Photo URL</span>
        <input
          type="url"
          value={photoUrl}
          onChange={(e) => {
            setPhotoFailed(false);
            onPhotoUrlChange(e.target.value);
          }}
          className="profile-input profile-input--mono"
          placeholder="https://…"
          autoComplete="photo"
        />
        <span className="profile-field__hint">Paste a public image URL. Preview updates above.</span>
      </label>

      <button
        type="button"
        onClick={onSave}
        disabled={saving}
        className="profile-btn profile-btn--primary profile-btn--block"
      >
        {saving ? 'Saving…' : 'Save identity'}
      </button>

      {showVerification || showReset ? (
        <div className="profile-actions">
          {showVerification ? (
            <button
              type="button"
              onClick={onSendVerification}
              disabled={sendingVerification}
              className="profile-btn profile-btn--ghost"
            >
              {sendingVerification ? 'Sending…' : 'Send verification email'}
            </button>
          ) : null}
          {showReset ? (
            <button
              type="button"
              onClick={onResetPassword}
              disabled={sendingReset}
              className="profile-btn profile-btn--ghost"
            >
              {sendingReset ? 'Sending…' : 'Reset password'}
            </button>
          ) : null}
        </div>
      ) : null}
    </ProfileSection>
  );
}

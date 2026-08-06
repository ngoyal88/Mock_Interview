import React from 'react';

type ProfileSaveBarProps = {
  dirty: boolean;
  saving: boolean;
  isComplete: boolean;
  onSave: () => void;
};

export function ProfileSaveBar({ dirty, saving, isComplete, onSave }: ProfileSaveBarProps) {
  return (
    <div className={`profile-save-bar${dirty ? ' profile-save-bar--dirty' : ''}`}>
      <div className="profile-save-bar__inner app-container">
        <div className="profile-save-bar__status">
          {dirty ? (
            <span className="profile-save-bar__dirty">Unsaved changes</span>
          ) : isComplete ? (
            <span className="profile-save-bar__synced">Preferences saved</span>
          ) : (
            <span className="profile-save-bar__hint">You can save partial preferences anytime</span>
          )}
        </div>
        <button
          type="button"
          className="profile-btn profile-btn--primary"
          disabled={saving}
          onClick={onSave}
        >
          {saving ? 'Saving…' : dirty ? 'Save changes' : 'Save preferences'}
        </button>
      </div>
    </div>
  );
}

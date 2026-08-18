import React, { type ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

type ProfileSectionVariant = 'default' | 'danger';

type ProfileSectionProps = {
  id?: string;
  icon: LucideIcon;
  title: string;
  description?: string;
  step?: number;
  children: ReactNode;
  variant?: ProfileSectionVariant;
};

export function ProfileSection({
  id,
  icon: Icon,
  title,
  description,
  step,
  children,
  variant = 'default',
}: ProfileSectionProps) {
  return (
    <section
      id={id}
      className={`profile-panel${variant === 'danger' ? ' profile-panel--danger' : ''}`}
    >
      <header className="profile-panel__header">
        {step != null ? (
          <span className="profile-panel__step" aria-hidden>
            {step}
          </span>
        ) : null}
        <div className="profile-panel__icon" aria-hidden>
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <h2 className="profile-panel__title">{title}</h2>
          {description ? <p className="profile-panel__description">{description}</p> : null}
        </div>
      </header>
      <div className="profile-panel__body">{children}</div>
    </section>
  );
}

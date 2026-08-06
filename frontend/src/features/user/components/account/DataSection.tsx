import React from 'react';
import { ChevronRight, Folder, FolderOpen, History, LineChart } from 'lucide-react';
import { Link } from 'react-router-dom';

import { AI_INTERVIEW_HISTORY_PATH } from 'features/interview/domain/modeContract';

import { ProfileSection } from './ProfileSection';

const DATA_LINKS = [
  {
    href: '/resume-vault',
    label: 'Resume Vault',
    description: 'Manage resumes and active profile context.',
    icon: FolderOpen,
  },
  {
    href: AI_INTERVIEW_HISTORY_PATH,
    label: 'Session history',
    description: 'Review transcripts and intelligence reports.',
    icon: History,
  },
  {
    href: '/signal-intelligence',
    label: 'Signal Intelligence',
    description: 'Verified claims, readiness, and profile memory.',
    icon: LineChart,
  },
] as const;

export function DataSection() {
  return (
    <ProfileSection
      icon={Folder}
      title="Your data"
      description="Jump to where your interview and profile data lives."
    >
      <ul className="profile-nav-list">
        {DATA_LINKS.map(({ href, label, description, icon: Icon }) => (
          <li key={href}>
            <Link to={href} className="profile-nav-item">
              <Icon className="profile-nav-item__icon" aria-hidden />
              <span className="min-w-0 flex-1">
                <span className="profile-nav-item__title">{label}</span>
                <span className="profile-nav-item__description">{description}</span>
              </span>
              <ChevronRight className="profile-nav-item__chevron" aria-hidden />
            </Link>
          </li>
        ))}
      </ul>
    </ProfileSection>
  );
}

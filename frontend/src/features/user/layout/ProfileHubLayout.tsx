import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';

import '../user.css';

const tabs = [
  { to: '/profile/preferences', label: 'Career preferences', shortLabel: 'Preferences' },
  { to: '/profile/account', label: 'Account', shortLabel: 'Account' },
] as const;

export function ProfileHubLayout() {
  const location = useLocation();
  const onPreferences = location.pathname.startsWith('/profile/preferences');

  return (
    <div className="profile-hub">
      <div className="app-container profile-hub__inner">
        <header className="profile-hub__header">
          <div className="profile-hub__header-copy min-w-0">
            <p className="profile-hub__eyebrow">Profile</p>
            <h1 className="profile-hub__title">
              {onPreferences ? 'Career preferences' : 'Account'}
            </h1>
            <p className="profile-hub__subtitle">
              {onPreferences
                ? 'Tell Vetta what you want next — interviews and job matches prefill from here.'
                : 'Identity, security, plan, and data controls for your workspace.'}
            </p>
          </div>
        </header>

        <nav className="profile-hub__tabs" aria-label="Profile sections">
          {tabs.map(({ to, label, shortLabel }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `profile-hub__tab${isActive ? ' profile-hub__tab--active' : ''}`
              }
            >
              <span className="hidden sm:inline">{label}</span>
              <span className="sm:hidden">{shortLabel}</span>
            </NavLink>
          ))}
        </nav>

        <Outlet />
      </div>
    </div>
  );
}

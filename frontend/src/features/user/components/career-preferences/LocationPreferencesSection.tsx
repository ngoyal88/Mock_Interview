import React from 'react';
import { MapPin, Plus, Trash2 } from 'lucide-react';

import { SUPPORTED_COUNTRIES, WORK_ARRANGEMENTS } from '../../types/careerPreferencesTypes';
import type { CareerPreferencesDoc, LocationRecord } from '../../types/careerPreferencesTypes';
import { ProfileSection } from '../account/ProfileSection';
import { ChoiceChipGroup } from '../shared/ChoiceChipGroup';
import { ProfileSwitchField } from '../shared/ProfileSwitchField';

type LocationPreferencesSectionProps = {
  form: CareerPreferencesDoc;
  onChange: (patch: Partial<CareerPreferencesDoc>) => void;
};

function emptyLocation(): LocationRecord {
  return { country: 'India', city: '', region: '' };
}

export function LocationPreferencesSection({ form, onChange }: LocationPreferencesSectionProps) {
  const updateLocation = (index: number, patch: Partial<LocationRecord>) => {
    const next = form.locations.map((loc, i) => (i === index ? { ...loc, ...patch } : loc));
    onChange({ locations: next });
  };

  return (
    <ProfileSection
      id="profile-section-location"
      step={2}
      icon={MapPin}
      title="Location & work mode"
      description="Where and how you want to work. Remote-only modes can skip city lists."
    >
      <ChoiceChipGroup
        label="Work arrangements"
        options={WORK_ARRANGEMENTS}
        selected={form.work_arrangements}
        onChange={(work_arrangements) => onChange({ work_arrangements })}
      />

      <ProfileSwitchField
        id="profile-willing-relocate"
        label="Willing to relocate"
        description="Signals openness to roles outside your listed locations."
        checked={Boolean(form.willing_to_relocate)}
        onChange={(willing_to_relocate) => onChange({ willing_to_relocate })}
      />

      <div className="profile-field">
        <div className="profile-field__row">
          <div>
            <span className="profile-field__label">Preferred locations</span>
            <p className="profile-field__hint">
              Add at least one unless you selected remote-only arrangements above.
            </p>
          </div>
          <button
            type="button"
            className="profile-btn profile-btn--secondary profile-btn--compact"
            onClick={() => onChange({ locations: [...form.locations, emptyLocation()] })}
          >
            <Plus className="h-4 w-4" aria-hidden />
            Add
          </button>
        </div>

        {form.locations.length === 0 ? (
          <div className="profile-empty-locations">
            <MapPin className="h-5 w-5" aria-hidden />
            <p>No locations yet</p>
          </div>
        ) : (
          <ul className="profile-location-list">
            {form.locations.map((loc, index) => (
              <li key={`loc-${index}`} className="profile-location-card">
                <div className="profile-location-card__grid">
                  <label className="profile-field">
                    <span className="profile-field__label">Country</span>
                    <select
                      value={loc.country}
                      onChange={(e) => updateLocation(index, { country: e.target.value })}
                      className="profile-input"
                    >
                      {SUPPORTED_COUNTRIES.map((country) => (
                        <option key={country} value={country}>
                          {country}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="profile-field">
                    <span className="profile-field__label">City</span>
                    <input
                      type="text"
                      value={loc.city ?? ''}
                      onChange={(e) => updateLocation(index, { city: e.target.value })}
                      className="profile-input"
                      placeholder="Optional…"
                      autoComplete="address-level2"
                    />
                  </label>
                  <label className="profile-field">
                    <span className="profile-field__label">Region / state</span>
                    <input
                      type="text"
                      value={loc.region ?? ''}
                      onChange={(e) => updateLocation(index, { region: e.target.value })}
                      className="profile-input"
                      placeholder="Optional…"
                      autoComplete="address-level1"
                    />
                  </label>
                </div>
                <button
                  type="button"
                  className="profile-btn profile-btn--ghost profile-btn--compact"
                  aria-label={`Remove location ${index + 1}`}
                  onClick={() => onChange({ locations: form.locations.filter((_, i) => i !== index) })}
                >
                  <Trash2 className="h-4 w-4" aria-hidden />
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </ProfileSection>
  );
}

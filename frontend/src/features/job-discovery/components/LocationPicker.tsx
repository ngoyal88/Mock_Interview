import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import { MapPin, Search, X } from 'lucide-react';

import {
  selectedLocationChips,
  suggestLocations,
  toggleLocationSelection,
  type LocationSuggestion,
} from '../utils/locationSuggest';

type LocationPickerProps = {
  selected: readonly string[];
  selectedCountries?: readonly string[];
  onChange: (next: { locationIds: string[]; countryCodes: string[] }) => void;
  mobile?: boolean;
};

export function LocationPicker({
  selected,
  selectedCountries = [],
  onChange,
  mobile = false,
}: LocationPickerProps) {
  const reactId = useId();
  const inputId = mobile ? `${reactId}-location-mobile` : `${reactId}-location`;
  const listboxId = `${inputId}-listbox`;
  const rootRef = useRef<HTMLFieldSetElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);

  const trimmed = query.trim();
  const suggestions = useMemo(() => (trimmed ? suggestLocations(trimmed) : []), [trimmed]);
  const chips = useMemo(
    () => selectedLocationChips(selected, selectedCountries),
    [selected, selectedCountries],
  );
  const listOpen = trimmed.length > 0;

  useEffect(() => {
    setActiveIndex(0);
  }, [trimmed]);

  useEffect(() => {
    if (!listOpen) return undefined;
    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setQuery('');
      }
    };
    document.addEventListener('mousedown', onPointerDown);
    return () => document.removeEventListener('mousedown', onPointerDown);
  }, [listOpen]);

  const applySuggestion = (suggestion: LocationSuggestion) => {
    onChange(toggleLocationSelection(selected, selectedCountries, suggestion));
    setQuery('');
    inputRef.current?.focus();
  };

  const removeChip = (chip: { locationIds: readonly string[]; countryCodes: readonly string[] }) => {
    if (chip.countryCodes.length) {
      onChange({
        locationIds: [...selected],
        countryCodes: selectedCountries.filter((code) => !chip.countryCodes.includes(code)),
      });
      return;
    }
    onChange({
      locationIds: selected.filter((id) => !chip.locationIds.includes(id)),
      countryCodes: [...selectedCountries],
    });
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Escape') {
      setQuery('');
      return;
    }
    if (event.key === 'Backspace' && !query && chips.length) {
      removeChip(chips[chips.length - 1]);
      return;
    }
    if (!listOpen || !suggestions.length) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex((index) => (index + 1) % suggestions.length);
      return;
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((index) => (index - 1 + suggestions.length) % suggestions.length);
      return;
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      const suggestion = suggestions[activeIndex];
      if (suggestion) applySuggestion(suggestion);
    }
  };

  const isActive = (suggestion: LocationSuggestion) => {
    if (suggestion.countryCodes.length) {
      return suggestion.countryCodes.every((code) => selectedCountries.includes(code));
    }
    return suggestion.locationIds.every((id) => selected.includes(id));
  };

  return (
    <fieldset ref={rootRef} className="jd-filter-field jd-location-picker">
      <legend className="jd-filter-label">Location</legend>

      {chips.length ? (
        <div className="jd-location-chips" aria-label="Selected locations">
          {chips.map((chip) => (
            <button
              key={chip.key}
              type="button"
              className="jd-location-chip"
              onClick={() => removeChip(chip)}
              aria-label={`Remove ${chip.label}`}
            >
              <MapPin className="jd-location-chip-icon" aria-hidden />
              <span>{chip.label}</span>
              <X className="jd-location-chip-x" aria-hidden />
            </button>
          ))}
        </div>
      ) : null}

      <div className="jd-location-combobox">
        <div className="jd-search-input-wrap jd-location-search-wrap">
          <Search className="jd-search-input-icon" aria-hidden />
          <input
            ref={inputRef}
            id={inputId}
            type="text"
            role="combobox"
            aria-expanded={listOpen}
            aria-controls={listboxId}
            aria-autocomplete="list"
            aria-activedescendant={
              listOpen && suggestions[activeIndex] ? `${listboxId}-${activeIndex}` : undefined
            }
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder={chips.length ? 'Add another…' : 'City or country'}
            className="jd-search-input"
            autoComplete="off"
            spellCheck={false}
          />
        </div>

        {listOpen ? (
          <div id={listboxId} className="jd-location-suggest" role="listbox" aria-label="Location suggestions">
            {suggestions.length ? (
              suggestions.map((suggestion, index) => {
                const active = isActive(suggestion);
                return (
                  <button
                    key={suggestion.key}
                    id={`${listboxId}-${index}`}
                    type="button"
                    role="option"
                    aria-selected={active}
                    className={`jd-location-option${active ? ' jd-location-option--active' : ''}${
                      index === activeIndex ? ' jd-location-option--focused' : ''
                    }`}
                    onMouseEnter={() => setActiveIndex(index)}
                    onClick={() => applySuggestion(suggestion)}
                  >
                    <span className="jd-location-option-label">{suggestion.label}</span>
                    <span className="jd-location-code">{suggestion.secondary}</span>
                  </button>
                );
              })
            ) : (
              <p className="jd-filter-hint jd-location-empty">No match</p>
            )}
          </div>
        ) : null}
      </div>
    </fieldset>
  );
}

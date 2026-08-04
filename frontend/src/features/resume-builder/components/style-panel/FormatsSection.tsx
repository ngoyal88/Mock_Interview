import type { StyleSpec } from '../../types/styleSpec';
import {
  BULLET_STYLE_OPTIONS,
  CONTACT_SEPARATOR_OPTIONS,
  DATE_FORMAT_OPTIONS,
  LINK_DISPLAY_OPTIONS,
} from '../../utils/styleOptionRegistry';
import BulletPreviewOption from './BulletPreviewOption';
import ContactSeparatorPreviewOption from './ContactSeparatorPreviewOption';
import DateFormatPreviewOption from './DateFormatPreviewOption';
import LinkDisplayPreviewOption from './LinkDisplayPreviewOption';
import StyleOptionGroup from './StyleOptionGroup';

type FormatsSectionProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
};

export default function FormatsSection({ styleSpec, disabled = false, onChange }: FormatsSectionProps) {
  return (
    <div className="rb-style-section__content">
      <StyleOptionGroup label="Dates">
        <div className="rb-style-option-grid rb-style-option-grid--3">
          {DATE_FORMAT_OPTIONS.map((option) => (
            <DateFormatPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.date_format === option.value}
              disabled={disabled}
              onSelect={() => onChange({ date_format: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>

      <StyleOptionGroup label="Links">
        <div className="rb-style-option-grid rb-style-option-grid--2">
          {LINK_DISPLAY_OPTIONS.map((option) => (
            <LinkDisplayPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.link_display === option.value}
              disabled={disabled}
              onSelect={() => onChange({ link_display: option.value })}
            />
          ))}
        </div>
      </StyleOptionGroup>

      <div className="rb-style-inline-field">
        <span className="rb-style-inline-field__label" id="style-separator-label">
          Separator
        </span>
        <div className="rb-style-inline-field__options" role="radiogroup" aria-labelledby="style-separator-label">
          {CONTACT_SEPARATOR_OPTIONS.map((option) => (
            <ContactSeparatorPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.contact_separator === option.value}
              disabled={disabled}
              onSelect={() => onChange({ contact_separator: option.value })}
            />
          ))}
        </div>
      </div>

      <div className="rb-style-inline-field">
        <span className="rb-style-inline-field__label" id="style-bullets-label">
          Bullets
        </span>
        <div className="rb-style-inline-field__options" role="radiogroup" aria-labelledby="style-bullets-label">
          {BULLET_STYLE_OPTIONS.map((option) => (
            <BulletPreviewOption
              key={option.value}
              option={option}
              selected={styleSpec.bullet_style === option.value}
              disabled={disabled}
              onSelect={() => onChange({ bullet_style: option.value })}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

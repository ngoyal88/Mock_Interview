import StyleOptionCard from './StyleOptionCard';
import type { PageSizeOption, MarginOption, DensityOption } from '../../utils/styleOptionRegistry';

type PageSizePreviewOptionProps = {
  option: PageSizeOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export function PageSizePreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: PageSizePreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      description={option.dimensions}
      onSelect={onSelect}
      className="rb-style-option-card--text"
    />
  );
}

type MarginPreviewOptionProps = {
  option: MarginOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export function MarginPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: MarginPreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      description={option.description}
      onSelect={onSelect}
      className="rb-style-option-card--text"
    />
  );
}

type DensityPreviewOptionProps = {
  option: DensityOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: () => void;
};

export function DensityPreviewOption({
  option,
  selected,
  disabled = false,
  onSelect,
}: DensityPreviewOptionProps) {
  return (
    <StyleOptionCard
      selected={selected}
      disabled={disabled}
      label={option.label}
      onSelect={onSelect}
      className="rb-style-option-card--density"
    >
      <span className="rb-density-preview" aria-hidden>
        {[0, 1, 2].map((index) => (
          <span
            key={index}
            className="rb-density-preview__line"
            style={{ marginBottom: `${option.lineGap}px` }}
          />
        ))}
      </span>
    </StyleOptionCard>
  );
}

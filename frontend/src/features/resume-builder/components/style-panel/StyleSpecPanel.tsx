import { useCallback, useState } from 'react';

import type { StyleSpec } from '../../types/styleSpec';
import { STYLE_SECTION_IDS, STYLE_SECTION_LABELS, type StyleSectionId } from '../../utils/styleOptionRegistry';

import ColorSection from './ColorSection';
import FormatsSection from './FormatsSection';
import LayoutSection from './LayoutSection';
import PageSetupSection from './PageSetupSection';
import StyleSection from './StyleSection';
import TypographySection from './TypographySection';

type StyleSpecPanelProps = {
  styleSpec: StyleSpec;
  disabled?: boolean;
  onChange: (patch: Partial<StyleSpec>) => void;
  onReset: () => void;
};

export default function StyleSpecPanel({
  styleSpec,
  disabled = false,
  onChange,
  onReset,
}: StyleSpecPanelProps) {
  const [expandedSections, setExpandedSections] = useState<Set<StyleSectionId>>(
    () => new Set<StyleSectionId>(['page_setup']),
  );

  const toggleSection = useCallback((sectionId: StyleSectionId) => {
    setExpandedSections((current) => {
      const next = new Set(current);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  }, []);

  const renderSectionBody = (sectionId: StyleSectionId) => {
    switch (sectionId) {
      case 'page_setup':
        return <PageSetupSection styleSpec={styleSpec} disabled={disabled} onChange={onChange} />;
      case 'formats':
        return <FormatsSection styleSpec={styleSpec} disabled={disabled} onChange={onChange} />;
      case 'layout':
        return <LayoutSection styleSpec={styleSpec} disabled={disabled} onChange={onChange} />;
      case 'color':
        return <ColorSection styleSpec={styleSpec} disabled={disabled} onChange={onChange} />;
      case 'typography':
        return <TypographySection styleSpec={styleSpec} disabled={disabled} onChange={onChange} />;
      default:
        return null;
    }
  };

  return (
    <div className="rb-style-panel">
      <div className="rb-style-panel__header">
        <button
          type="button"
          disabled={disabled}
          onClick={onReset}
          className="rb-style-panel__reset"
        >
          Reset defaults
        </button>
      </div>

      <div className="rb-style-panel__sections">
        {STYLE_SECTION_IDS.map((sectionId) => (
          <StyleSection
            key={sectionId}
            id={`style-${sectionId}`}
            title={STYLE_SECTION_LABELS[sectionId]}
            expanded={expandedSections.has(sectionId)}
            onToggle={() => toggleSection(sectionId)}
          >
            {renderSectionBody(sectionId)}
          </StyleSection>
        ))}
      </div>
    </div>
  );
}

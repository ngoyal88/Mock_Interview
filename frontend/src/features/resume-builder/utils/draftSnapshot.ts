import type { ResumeProfile } from 'features/vault/types/domain';

import type { StyleSpec } from '../types/styleSpec';
import { DEFAULT_STYLE_SPEC } from '../types/styleSpec';
import type { BuilderCustomSection, BuilderSection, ResumeBuilderDraft } from '../types/resumeBuilder';

export type DraftSnapshot = {
  profile: ResumeProfile;
  section_layout: BuilderSection[];
  custom_sections: BuilderCustomSection[];
  style_spec: StyleSpec;
};

function cloneProfile(profile: ResumeProfile): ResumeProfile {
  return JSON.parse(JSON.stringify(profile)) as ResumeProfile;
}

export function captureDraftSnapshot(draft: ResumeBuilderDraft): DraftSnapshot {
  return {
    profile: cloneProfile(draft.profile),
    section_layout: JSON.parse(JSON.stringify(draft.section_layout)) as BuilderSection[],
    custom_sections: JSON.parse(JSON.stringify(draft.custom_sections)) as BuilderCustomSection[],
    style_spec: JSON.parse(JSON.stringify(draft.style_spec ?? DEFAULT_STYLE_SPEC)) as StyleSpec,
  };
}

export function applyDraftSnapshot(draft: ResumeBuilderDraft, snapshot: DraftSnapshot): ResumeBuilderDraft {
  return {
    ...draft,
    profile: cloneProfile(snapshot.profile),
    section_layout: JSON.parse(JSON.stringify(snapshot.section_layout)) as BuilderSection[],
    custom_sections: JSON.parse(JSON.stringify(snapshot.custom_sections)) as BuilderCustomSection[],
    style_spec: JSON.parse(JSON.stringify(snapshot.style_spec)) as StyleSpec,
  };
}

export function snapshotsEqual(a: DraftSnapshot, b: DraftSnapshot): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

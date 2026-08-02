import type { ResumeProfile } from 'features/vault/types/domain';

import type { StyleSpec } from './styleSpec';
import { DEFAULT_STYLE_SPEC } from './styleSpec';

export type BuilderSectionKind =
  | 'identity'
  | 'summary'
  | 'work_experience'
  | 'education'
  | 'skills'
  | 'projects'
  | 'achievements'
  | 'publications'
  | 'custom';

export interface BuilderSection {
  id: string;
  kind: BuilderSectionKind;
  label: string;
  enabled: boolean;
}

export interface BuilderCustomSection {
  id: string;
  title: string;
  content: string;
}

export interface ResumeBuilderDraft {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
  updated_at: string;
  template_id: string;
  template_version: string;
  profile: ResumeProfile;
  section_layout: BuilderSection[];
  custom_sections: BuilderCustomSection[];
  target_resume_id?: string | null;
  source_resume_id?: string | null;
  source_version_id?: string | null;
  source_kind?: 'blank' | 'vault_fork' | 'linkedin_import';
  source_linkedin_url?: string | null;
  style_spec: StyleSpec;
  status: 'draft';
}

export interface LinkedInImportPayload {
  input: string;
  template_id?: string;
}

export interface LinkedInImportResponse {
  linkedin_url: string;
  profile: ResumeProfile;
  draft: ResumeBuilderDraft | null;
  warnings: string[];
}

export interface DraftResponse {
  draft: ResumeBuilderDraft;
}

export interface DraftListResponse {
  drafts: ResumeBuilderDraft[];
}

export interface TemplateSectionConfig {
  fields: string[];
}

export interface TemplateMetadata {
  id: string;
  version: string;
  display_name?: string;
  description: string;
  status: 'live' | 'coming_soon';
  tags: string[];
  preview_asset: string;
  supports_flexible_sections: boolean;
  sections?: Partial<Record<BuilderSectionKind, TemplateSectionConfig>>;
}

export interface TemplateListResponse {
  templates: TemplateMetadata[];
}

export { DEFAULT_STYLE_SPEC };
export type { StyleSpec } from './styleSpec';

export interface ResumeBuilderHealthResponse {
  enabled: boolean;
  compile_ok: boolean;
}

export interface CreateDraftPayload {
  template_id?: string;
  resume_id?: string;
  version_id?: string;
  profile?: ResumeProfile;
}

export interface SaveDraftPayload {
  name: string;
  profile: ResumeProfile;
  section_layout: BuilderSection[];
  custom_sections: BuilderCustomSection[];
  target_resume_id?: string | null;
  style_spec?: StyleSpec;
}

export interface DraftPatchPayload {
  name?: string;
  template_id?: string;
  style_spec?: StyleSpec;
}

export interface PublishDraftPayload {
  user_note?: string;
  target_resume_id?: string | null;
  resume_name?: string | null;
  tags?: string[];
  set_active?: boolean;
}

export interface PublishDraftResponse {
  resume_id: string;
  version_id: string;
  entry: {
    id: string;
    name?: string;
    origin?: 'upload' | 'builder';
    current_version_id?: string | null;
  };
  version: {
    id: string;
    resume_id?: string;
    version_number?: number;
  };
  scorecard: {
    score?: number;
    summary_line?: string;
  };
}


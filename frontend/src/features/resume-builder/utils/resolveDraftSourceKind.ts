import type { ResumeBuilderDraft } from '../types/resumeBuilder';

export type DraftSourceKind = 'blank' | 'vault_fork' | 'linkedin_import';

export function resolveDraftSourceKind(draft: ResumeBuilderDraft): DraftSourceKind {
  if (draft.source_kind) return draft.source_kind;
  return draft.source_resume_id ? 'vault_fork' : 'blank';
}

export function draftSourceLabel(kind: DraftSourceKind): string {
  if (kind === 'vault_fork') return 'From Vault';
  if (kind === 'linkedin_import') return 'From LinkedIn';
  return 'Blank';
}

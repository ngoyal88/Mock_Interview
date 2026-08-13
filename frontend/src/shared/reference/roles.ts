/** Mirrors backend `services.platform.reference.roles` — product role picker catalog. */

export type SupportedRole = {
  id: string;
  label: string;
  aliases?: readonly string[];
};

export const SUPPORTED_ROLES: readonly SupportedRole[] = [
  { id: 'software_engineer', label: 'Software Engineer', aliases: ['SWE', 'SDE'] },
  { id: 'frontend_engineer', label: 'Frontend Engineer' },
  { id: 'backend_engineer', label: 'Backend Engineer' },
  { id: 'full_stack_engineer', label: 'Full Stack Engineer' },
  { id: 'mobile_engineer', label: 'Mobile Engineer' },
  { id: 'android_engineer', label: 'Android Engineer' },
  { id: 'ios_engineer', label: 'iOS Engineer' },
  { id: 'devops_engineer', label: 'DevOps Engineer' },
  { id: 'site_reliability_engineer', label: 'Site Reliability Engineer', aliases: ['SRE'] },
  { id: 'cloud_engineer', label: 'Cloud Engineer' },
  { id: 'platform_engineer', label: 'Platform Engineer' },
  { id: 'data_engineer', label: 'Data Engineer' },
  { id: 'machine_learning_engineer', label: 'Machine Learning Engineer', aliases: ['ML Engineer'] },
  { id: 'ai_engineer', label: 'AI Engineer' },
  { id: 'data_scientist', label: 'Data Scientist' },
  { id: 'data_analyst', label: 'Data Analyst' },
  { id: 'product_engineer', label: 'Product Engineer' },
  { id: 'qa_engineer', label: 'QA Engineer' },
  { id: 'security_engineer', label: 'Security Engineer' },
  { id: 'system_design_architecture', label: 'System Design / Architecture' },
  { id: 'engineering_manager', label: 'Engineering Manager' },
  { id: 'product_manager', label: 'Product Manager', aliases: ['PM'] },
  { id: 'technical_program_manager', label: 'Technical Program Manager', aliases: ['TPM'] },
  { id: 'business_analyst', label: 'Business Analyst' },
];

export const ROLE_LABELS = SUPPORTED_ROLES.map((role) => role.label);

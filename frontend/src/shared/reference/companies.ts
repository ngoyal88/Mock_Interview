/** Mirrors backend `services.platform.reference.companies` — product company picker catalog.

`id` is the stable slug for prefs `target_company_slugs` / Job Discovery filters.
`label` is the interview / UI display name.
*/
export type SupportedCompany = {
  id: string;
  label: string;
  aliases?: readonly string[];
};

export const SUPPORTED_COMPANIES: readonly SupportedCompany[] = [
  { id: 'google', label: 'Google' },
  { id: 'microsoft', label: 'Microsoft' },
  { id: 'amazon', label: 'Amazon' },
  { id: 'meta', label: 'Meta', aliases: ['Facebook'] },
  { id: 'apple', label: 'Apple' },
  { id: 'netflix', label: 'Netflix' },
  { id: 'uber', label: 'Uber' },
  { id: 'airbnb', label: 'Airbnb' },
  { id: 'stripe', label: 'Stripe' },
  { id: 'atlassian', label: 'Atlassian' },
  { id: 'salesforce', label: 'Salesforce' },
  { id: 'adobe', label: 'Adobe' },
  { id: 'oracle', label: 'Oracle' },
  { id: 'ibm', label: 'IBM' },
  { id: 'nvidia', label: 'Nvidia' },
  { id: 'tesla', label: 'Tesla' },
  { id: 'openai', label: 'OpenAI' },
  { id: 'anthropic', label: 'Anthropic' },
  { id: 'databricks', label: 'Databricks' },
  { id: 'snowflake', label: 'Snowflake' },
  { id: 'palantir', label: 'Palantir' },
  { id: 'bloomberg', label: 'Bloomberg' },
  { id: 'goldman-sachs', label: 'Goldman Sachs' },
  { id: 'jpmorgan-chase', label: 'JPMorgan Chase', aliases: ['JPMorgan', 'Chase'] },
  { id: 'walmart-global-tech', label: 'Walmart Global Tech' },
  { id: 'flipkart', label: 'Flipkart' },
  { id: 'phonepe', label: 'PhonePe' },
  { id: 'razorpay', label: 'Razorpay' },
  { id: 'zomato', label: 'Zomato' },
  { id: 'swiggy', label: 'Swiggy' },
  { id: 'cred', label: 'CRED' },
  { id: 'meesho', label: 'Meesho' },
  { id: 'zoho', label: 'Zoho' },
  { id: 'freshworks', label: 'Freshworks' },
  { id: 'tcs', label: 'TCS', aliases: ['Tata Consultancy Services'] },
  { id: 'infosys', label: 'Infosys' },
  { id: 'wipro', label: 'Wipro' },
  { id: 'accenture', label: 'Accenture' },
  { id: 'deloitte', label: 'Deloitte' },
];

export const COMPANY_LABELS = SUPPORTED_COMPANIES.map((company) => company.label);
export const COMPANY_SLUGS = SUPPORTED_COMPANIES.map((company) => company.id);

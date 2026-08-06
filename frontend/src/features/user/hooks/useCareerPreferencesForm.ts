import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';

import { useCareerPreferencesMutation } from '../mutations/useCareerPreferencesMutation';
import { useCareerPreferencesQuery } from '../queries/useCareerPreferencesQuery';
import type { CareerPreferencesDoc, CareerPreferencesPatch } from '../types/careerPreferencesTypes';
import { emptyCareerPreferences } from '../types/careerPreferencesTypes';

function toPatch(form: CareerPreferencesDoc): CareerPreferencesPatch {
  return {
    target_titles: form.target_titles,
    exclude_titles: form.exclude_titles,
    experience_levels: form.experience_levels,
    years_experience: form.years_experience,
    locations: form.locations.map(({ country, city, region }) => ({
      country,
      city: city?.trim() || undefined,
      region: region?.trim() || undefined,
    })),
    exclude_locations: form.exclude_locations,
    work_arrangements: form.work_arrangements,
    willing_to_relocate: form.willing_to_relocate,
    employment_types: form.employment_types,
    visa_sponsorship_required: form.visa_sponsorship_required,
    language: form.language,
    salary_min: form.salary_min,
    salary_max: form.salary_max,
    salary_currency: form.salary_currency,
    company_size_buckets: form.company_size_buckets,
    target_company_slugs: form.target_company_slugs,
    target_industries: form.target_industries,
    exclude_staffing_agencies: form.exclude_staffing_agencies,
  };
}

export function useCareerPreferencesForm() {
  const { data, loading, completeness } = useCareerPreferencesQuery();
  const mutation = useCareerPreferencesMutation();
  const [form, setForm] = useState<CareerPreferencesDoc>(emptyCareerPreferences());
  const [initialized, setInitialized] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (data?.preferences) {
      setForm(data.preferences);
    } else {
      setForm(emptyCareerPreferences());
    }
    setInitialized(true);
    setDirty(false);
  }, [data, loading]);

  // ponytail: BrowserRouter has no useBlocker; tab close/refresh only. In-app leave
  // guard needs createBrowserRouter + RouterProvider if we want confirm-on-navigate.
  useEffect(() => {
    if (!dirty) return undefined;
    const onBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, [dirty]);

  const updateForm = useCallback((patch: Partial<CareerPreferencesDoc>) => {
    setForm((prev) => ({ ...prev, ...patch }));
    setDirty(true);
  }, []);

  const save = useCallback(async () => {
    try {
      const response = await mutation.mutateAsync(toPatch(form));
      setForm(response.preferences);
      setDirty(false);
      toast.success('Career preferences saved');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to save preferences');
    }
  }, [form, mutation]);

  const displayCompleteness = dirty
    ? completeness
    : data?.completeness ?? completeness;

  return {
    form,
    updateForm,
    save,
    saving: mutation.isPending,
    loading: loading || !initialized,
    dirty,
    completeness: displayCompleteness,
  };
}

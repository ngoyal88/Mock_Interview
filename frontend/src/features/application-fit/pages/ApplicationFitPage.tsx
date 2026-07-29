import '../application-fit.css';
import { useState } from 'react';

import { ResumePreviewOverlay } from 'features/application-fit/components/input/ResumePreviewOverlay';
import { JD_FILE_ACCEPT } from 'shared/utils/jdInputUtils';
import AppPageShell from 'shared/ui/AppPageShell';
import { ApplicationFitLoadingCard } from '../components/loading/ApplicationFitLoadingCard';
import { JobDescriptionPanel } from '../components/input/JobDescriptionPanel';
import { ResumeContextCard } from '../components/input/ResumeContextCard';
import { TargetDetailsForm } from '../components/input/TargetDetailsForm';
import { ApplicationFitReport } from '../components/report/ApplicationFitReport';
import { useApplicationFit } from '../hooks/useApplicationFit';

export default function ApplicationFitPage() {
  const [resumePreviewOpen, setResumePreviewOpen] = useState(false);
  const {
    view,
    targetRole,
    setTargetRole,
    targetCompany,
    setTargetCompany,
    jobDescription,
    setJobDescription,
    report,
    canAnalyze,
    resumeLoading,
    entry,
    version,
    analyzeFit,
    analyzeAgain,
    fileInputRef,
    jdUploading,
    handleJdUploadClick,
    handleJdFileChange,
  } = useApplicationFit();

  if (view === 'loading') {
    return (
      <div className="application-fit-page">
        <div className="relative min-h-[calc(100vh-4rem)] pb-14 pt-10">
          <div className="app-container flex min-h-[60vh] items-center justify-center">
            <ApplicationFitLoadingCard />
          </div>
        </div>
      </div>
    );
  }

  if (view === 'report' && report) {
    return (
      <div className="application-fit-page application-fit-report">
        <div className="app-container relative z-10 mx-auto flex max-w-[72rem] flex-col gap-5 py-8">
          <ApplicationFitReport
            report={report}
            targetRole={targetRole}
            targetCompany={targetCompany}
            jobDescription={jobDescription}
            onAnalyzeAgain={analyzeAgain}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="application-fit-page">
      <AppPageShell
        maxWidthClass="max-w-[72rem]"
        title="Application Fit"
        subtitle="See where you pass ATS, recruiter scan, and HM review — before you apply."
      >
        <div className="grid grid-cols-1 items-stretch gap-4 lg:grid-cols-12 lg:gap-5">
          <div className="flex flex-col gap-4 lg:col-span-5">
            <ResumeContextCard
              entry={entry}
              version={version}
              loading={resumeLoading}
              onPreviewResume={() => setResumePreviewOpen(true)}
            />
            <TargetDetailsForm
              targetRole={targetRole}
              targetCompany={targetCompany}
              onRoleChange={setTargetRole}
              onCompanyChange={setTargetCompany}
            />
          </div>
          <div className="flex min-h-[420px] flex-col lg:col-span-7 lg:min-h-[28rem]">
            <JobDescriptionPanel
              value={jobDescription}
              onChange={setJobDescription}
              onClear={() => setJobDescription('')}
              onUploadClick={handleJdUploadClick}
              uploading={jdUploading}
              canAnalyze={canAnalyze}
              onAnalyze={() => void analyzeFit()}
            />
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept={JD_FILE_ACCEPT}
          className="hidden"
          onChange={(event) => void handleJdFileChange(event)}
        />

        <ResumePreviewOverlay
          open={resumePreviewOpen}
          onClose={() => setResumePreviewOpen(false)}
          version={version}
          entryName={version?.source_filename || entry?.name || 'Resume'}
        />
      </AppPageShell>
    </div>
  );
}

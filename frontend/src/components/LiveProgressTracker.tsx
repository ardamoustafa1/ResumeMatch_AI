import { Activity, CheckCircle2, AlertCircle } from 'lucide-react';

interface ProgressData {
  step: string;
  progress: number;
  data?: any;
}

interface LiveProgressTrackerProps {
  progress: ProgressData | null;
  error: string | null;
}

export const LiveProgressTracker = ({ progress, error }: LiveProgressTrackerProps) => {
  if (!progress && !error) return null;

  const currentProgress = progress?.progress || 0;
  const isComplete = currentProgress === 100;
  const isError = !!error || progress?.step === 'failed';
  
  let statusText = "Initializing...";
  if (isError) statusText = "Analysis Failed";
  else if (isComplete) statusText = "Analysis Complete!";
  else if (progress?.step === 'validating') statusText = "Validating Inputs...";
  else if (progress?.step === 'analyzing_match') statusText = "Calculating Match Score...";
  else if (progress?.step === 'generating_messages') statusText = "Crafting Outreach Messages...";
  else if (progress?.step === 'improving_profile') statusText = "Generating Profile Tips...";

  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '24px', marginTop: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        {isError ? (
          <AlertCircle color="var(--accent-error)" />
        ) : isComplete ? (
          <CheckCircle2 color="var(--accent-success)" />
        ) : (
          <Activity color="var(--accent-blue)" className="animate-pulse-slow" />
        )}
        <h3 style={{ fontSize: '1.1rem', margin: 0 }}>{statusText}</h3>
        
        {!isComplete && !isError && (
          <span style={{ marginLeft: 'auto', fontWeight: 'bold', color: 'var(--accent-blue)' }}>
            {currentProgress}%
          </span>
        )}
      </div>

      <div style={{ 
        width: '100%', 
        height: '8px', 
        background: 'rgba(255,255,255,0.05)', 
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <div style={{
          height: '100%',
          width: `${currentProgress}%`,
          background: isError ? 'var(--accent-error)' : isComplete ? 'var(--accent-success)' : 'linear-gradient(90deg, var(--accent-blue), var(--accent-purple))',
          borderRadius: '4px',
          transition: 'width 0.5s ease-out, background 0.3s ease'
        }} />
      </div>

      {isError && (
        <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: 'var(--accent-error)', fontSize: '0.9rem' }}>
          {error || progress?.data?.error || "An unknown error occurred"}
        </div>
      )}
    </div>
  );
};

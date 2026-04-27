import { useState } from 'react';
import { Target, MessageSquare, Lightbulb, Copy, Check } from 'lucide-react';

interface ResultsDashboardProps {
  data: any;
}

export const ResultsDashboard = ({ data }: ResultsDashboardProps) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!data) return null;

  const matchScore = data.match_result?.match_score || 0;
  const matchReasoning = data.match_result?.reasoning || "";
  const keyStrengths = data.match_result?.key_strengths || [];
  const missingSkills = data.match_result?.missing_skills || [];
  
  const messages = data.outreach_messages?.messages || [];
  const improvements = data.profile_improvements?.improvements || [];

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="animate-fade-in" style={{ marginTop: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Match Score Section */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Target color="var(--accent-success)" size={24} />
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Match Analysis</h2>
        </div>
        
        <div className="grid-2" style={{ alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <svg viewBox="0 0 36 36" className="circular-chart">
              <path className="circle-bg"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path className="circle"
                stroke={matchScore >= 70 ? 'var(--accent-success)' : matchScore >= 40 ? '#F59E0B' : 'var(--accent-error)'}
                strokeDasharray={`${matchScore}, 100`}
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <text x="18" y="20.35" className="percentage">{matchScore}%</text>
            </svg>
          </div>
          
          <div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>{matchReasoning}</p>
            
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>Key Strengths</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {keyStrengths.map((s: string, i: number) => (
                  <span key={i} style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-success)', padding: '4px 10px', borderRadius: '16px', fontSize: '0.85rem' }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
            
            {missingSkills.length > 0 && (
              <div>
                <h4 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>Missing Skills</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {missingSkills.map((s: string, i: number) => (
                    <span key={i} style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-error)', padding: '4px 10px', borderRadius: '16px', fontSize: '0.85rem' }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Outreach Messages */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <MessageSquare color="var(--accent-blue)" size={24} />
          <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Outreach Messages</h2>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map((msg: any, i: number) => (
            <div key={i} className="glass-card" style={{ padding: '20px', position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <span style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase' }}>
                  {msg.platform} - {msg.tone}
                </span>
                
                <button 
                  onClick={() => handleCopy(msg.content, i)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
                >
                  {copiedIndex === i ? <Check size={16} color="var(--accent-success)" /> : <Copy size={16} />}
                  {copiedIndex === i ? 'Copied' : 'Copy'}
                </button>
              </div>
              
              <div style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap', fontFamily: 'var(--font-sans)', fontSize: '0.95rem' }}>
                {msg.content}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Profile Improvements */}
      {improvements.length > 0 && (
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <Lightbulb color="var(--accent-purple)" size={24} />
            <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Profile Improvements</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {improvements.map((imp: any, i: number) => (
              <div key={i} className="glass-card" style={{ padding: '16px', borderLeft: '4px solid var(--accent-purple)' }}>
                <h4 style={{ color: 'var(--text-primary)', marginBottom: '8px', fontSize: '1.05rem' }}>{imp.suggestion}</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '12px' }}>{imp.reasoning}</p>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', fontSize: '0.85rem' }}>
                  <strong>Example: </strong> <span style={{ color: 'var(--text-muted)' }}>{imp.example}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
    </div>
  );
};

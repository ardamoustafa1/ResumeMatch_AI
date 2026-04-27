import { useState, useRef } from 'react';
import { Send, FileText, Briefcase, Building, User, UploadCloud, Loader2 } from 'lucide-react';

interface InputFormProps {
  onSubmit: (data: { cv_text: string; jd_text: string; company: string; recruiter_name: string }) => void;
  isLoading: boolean;
}

export const InputForm = ({ onSubmit, isLoading }: InputFormProps) => {
  const [cvText, setCvText] = useState('');
  const [jdText, setJdText] = useState('');
  const [company, setCompany] = useState('');
  const [recruiterName, setRecruiterName] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsExtracting(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/extract-text`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to extract text');
      }

      const data = await res.json();
      setCvText(data.extracted_text);
    } catch (err: any) {
      alert(`Extraction failed: ${err.message}`);
    } finally {
      setIsExtracting(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: any) => {
    e.preventDefault();
    if (!cvText || !jdText) return;
    onSubmit({ cv_text: cvText, jd_text: jdText, company, recruiter_name: recruiterName });
  };

  return (
    <div className="glass-panel" style={{ padding: '32px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Start Analysis</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Provide the candidate's CV and the Job Description to generate a tailored outreach strategy.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid-2">
          <div className="input-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: 0 }}>
                <FileText size={16} color="var(--accent-blue)" /> Candidate CV
              </label>
              
              <button 
                type="button" 
                onClick={() => fileInputRef.current?.click()}
                disabled={isExtracting}
                style={{ 
                  display: 'flex', alignItems: 'center', gap: '6px', 
                  background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)', 
                  border: '1px solid rgba(59, 130, 246, 0.2)', padding: '4px 10px', 
                  borderRadius: '6px', fontSize: '0.8rem', cursor: isExtracting ? 'not-allowed' : 'pointer' 
                }}
              >
                {isExtracting ? <Loader2 size={14} className="animate-spin" /> : <UploadCloud size={14} />}
                {isExtracting ? 'Extracting...' : 'Upload PDF/Image'}
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                accept=".pdf,image/png,image/jpeg,image/jpg" 
                style={{ display: 'none' }} 
              />
            </div>
            
            <textarea
              className="premium-input"
              style={{ minHeight: '200px', resize: 'vertical' }}
              placeholder="Paste the candidate's full CV here, or upload a PDF/Image..."
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Briefcase size={16} color="var(--accent-purple)" /> Job Description
            </label>
            <textarea
              className="premium-input"
              style={{ minHeight: '200px', resize: 'vertical' }}
              placeholder="Paste the target Job Description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="grid-2" style={{ marginTop: '16px' }}>
          <div className="input-group">
            <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Building size={16} color="var(--accent-pink)" /> Target Company (Optional)
            </label>
            <input
              type="text"
              className="premium-input"
              placeholder="e.g. Stripe, Google, Acme Corp"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label className="input-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <User size={16} color="var(--accent-success)" /> Recruiter Name (Optional)
            </label>
            <input
              type="text"
              className="premium-input"
              placeholder="e.g. Sarah Connor"
              value={recruiterName}
              onChange={(e) => setRecruiterName(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px' }}>
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={isLoading || !cvText || !jdText}
          >
            {isLoading ? (
              <>
                <div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                Initializing...
              </>
            ) : (
              <>
                <Send size={18} /> Run AI Engine
              </>
            )}
          </button>
        </div>
      </form>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

import { useState, useEffect, useRef } from 'react';
import { Layout } from './components/Layout';
import { InputForm } from './components/InputForm';
import { LiveProgressTracker } from './components/LiveProgressTracker';
import { ResultsDashboard } from './components/ResultsDashboard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws');

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const handleSubmit = async (data: any) => {
    setIsLoading(true);
    setProgress(null);
    setError(null);
    setResults(null);
    
    // Add dummy user_id required by backend
    const requestData = {
      ...data,
      user_id: "00000000-0000-0000-0000-000000000000"
    };

    try {
      const res = await fetch(`${API_URL}/api/v1/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
      
      if (!res.ok) {
        throw new Error('Failed to start analysis');
      }
      
      const { analysis_id } = await res.json();
      connectWebSocket(analysis_id);
    } catch (err: any) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  const connectWebSocket = (analysisId: string) => {
    if (wsRef.current) wsRef.current.close();
    
    const ws = new WebSocket(`${WS_URL}/ws/analysis/${analysisId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.step === 'heartbeat') return;
      
      setProgress(data);
      
      if (data.step === 'done') {
        setResults(data.data);
        setIsLoading(false);
        ws.close();
      } else if (data.step === 'failed') {
        setError(data.data?.error || 'Analysis failed');
        setIsLoading(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setError('WebSocket connection error');
      setIsLoading(false);
    };
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return (
    <Layout>
      {!results ? (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
          <LiveProgressTracker progress={progress} error={error} />
        </div>
      ) : (
        <div>
          <button 
            onClick={() => { setResults(null); setProgress(null); }}
            className="btn btn-secondary"
            style={{ marginBottom: '24px' }}
          >
            ← Start New Analysis
          </button>
          <ResultsDashboard data={results} />
        </div>
      )}
    </Layout>
  );
}

export default App;

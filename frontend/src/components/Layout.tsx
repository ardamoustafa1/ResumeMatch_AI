import { Network, Code2, Zap } from 'lucide-react';

export const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div style={{ paddingBottom: '60px' }}>
      <header className="glass-panel" style={{ position: 'sticky', top: 0, zIndex: 100, borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none', padding: '16px 0', marginBottom: '40px' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', padding: '8px', borderRadius: '12px' }}>
              <Network color="white" size={24} />
            </div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
              Network<span className="text-gradient">Forge</span>
            </h1>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.05)', padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border-color)' }}>
              <Zap size={14} color="var(--accent-purple)" />
              Powered by Groq 70B
            </div>
            <a href="https://github.com/ardamoustafa1/NetworkForge" target="_blank" rel="noreferrer" style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex' }}>
              <Code2 size={24} />
            </a>
          </div>
        </div>
      </header>

      <main className="container animate-fade-in">
        {children}
      </main>
    </div>
  );
};

import { Link } from 'react-router-dom'
import { GitBranch, Terminal, Search, FileText, Plus } from 'lucide-react'

const features = [
  { icon: <Terminal size={20} />, title: 'AI File Push', desc: 'Push files with AI-generated commit messages' },
  { icon: <Search size={20} />, title: 'Deep Analyzer', desc: 'Health scores and architectural reports' },
  { icon: <FileText size={20} />, title: 'README Generator', desc: 'Professional docs in multiple styles' },
  { icon: <Plus size={20} />, title: 'Repo Creator', desc: 'Create GitHub repositories instantly' },
]

export default function Landing() {
  const copyInstall = () => {
    navigator.clipboard.writeText('pip install aga-ai-github-assistant')
    alert('Copied!')
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0d1117', color: 'white', fontFamily: 'sans-serif' }}>
      {/* Navbar */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 32px', borderBottom: '1px solid #21262d' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 'bold', fontSize: 18 }}>
          <GitBranch size={22} />
          AGA
        </div>
        <Link to="/auth">
          <button style={{ background: 'white', color: 'black', padding: '6px 16px', borderRadius: 6, fontWeight: 600, border: 'none', cursor: 'pointer' }}>
            Get Started
          </button>
        </Link>
      </nav>

      {/* Hero */}
      <div style={{ textAlign: 'center', padding: '60px 16px 20px' }}>
        <div style={{ display: 'inline-block', background: '#1f6feb22', color: '#58a6ff', fontSize: 12, padding: '4px 12px', borderRadius: 20, border: '1px solid #1f6feb55', marginBottom: 20 }}>
          Powered by Groq · Llama 3.3 70B
        </div>
        <h1 style={{ fontSize: 44, fontWeight: 800, lineHeight: 1.2, marginBottom: 16 }}>
          Your AI-Powered <span style={{ color: '#58a6ff' }}>GitHub Assistant</span>
        </h1>
        <p style={{ color: '#8b949e', fontSize: 16, maxWidth: 480, margin: '0 auto 28px' }}>
          Push files, analyze repos, generate READMEs, and create repositories — all from one place.
        </p>

        {/* Buttons */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 24 }}>
          <Link to="/auth">
            <button style={{ background: '#238636', color: 'white', padding: '10px 24px', borderRadius: 6, fontWeight: 600, border: 'none', cursor: 'pointer' }}>
              Launch App
            </button>
          </Link>
          <a href="https://pypi.org/project/aga-ai-github-assistant/" target="_blank" rel="noreferrer">
            <button style={{ background: 'transparent', color: 'white', padding: '10px 24px', borderRadius: 6, fontWeight: 600, border: '1px solid #30363d', cursor: 'pointer' }}>
              View on PyPI
            </button>
          </a>
        </div>

        {/* Install command */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: '12px 20px', marginBottom: 40 }}>
          <code style={{ color: '#58a6ff', fontSize: 14 }}>pip install aga-ai-github-assistant</code>
          <button onClick={copyInstall} style={{ background: 'transparent', color: '#8b949e', border: '1px solid #30363d', borderRadius: 4, padding: '4px 10px', fontSize: 12, cursor: 'pointer' }}>
            Copy
          </button>
        </div>

        {/* Features */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, maxWidth: 900, margin: '0 auto', padding: '0 16px' }}>
          {features.map((f) => (
            <div key={f.title} style={{ background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: 16, textAlign: 'left' }}>
              <div style={{ color: '#58a6ff', marginBottom: 8 }}>{f.icon}</div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{f.title}</div>
              <div style={{ color: '#8b949e', fontSize: 12, marginTop: 4 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      <footer style={{ textAlign: 'center', color: '#8b949e', fontSize: 12, padding: '24px', borderTop: '1px solid #21262d', marginTop: 40 }}>
        AGA v1.3.1 · Built with FastAPI + React
      </footer>
    </div>
  )
}

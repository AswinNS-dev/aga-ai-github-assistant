import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { listRepos } from '../lib/api'
import { useNavigate } from 'react-router-dom'
import { FolderGit2, Search, FileText, Plus, Star, Lock, Globe } from 'lucide-react'

const quickActions = [
  { label: 'Push Files', icon: <FolderGit2 size={18} />, to: '/repo-manager' },
  { label: 'Analyze Repo', icon: <Search size={18} />, to: '/analyzer' },
  { label: 'Generate README', icon: <FileText size={18} />, to: '/readme' },
  { label: 'Create Repo', icon: <Plus size={18} />, to: '/create-repo' },
]

export default function Dashboard() {
  const { auth } = useAuth()
  const navigate = useNavigate()
  const [repos, setRepos] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [history] = useState(() => JSON.parse(sessionStorage.getItem('aga_history') || '[]'))

  useEffect(() => {
    listRepos(auth.github_token, auth.groq_key)
      .then((r) => setRepos(r.data))
      .finally(() => setLoading(false))
  }, [])

  const filtered = repos.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase())
  )

  const getGreeting = () => {
    const hour = new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata', hour: 'numeric', hour12: false })
    const h = parseInt(hour)
    if (h < 12) return 'Good Morning'
    if (h < 17) return 'Good Afternoon'
    return 'Good Evening'
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">{getGreeting()}, {auth.name} 👋</h1>
        <p className="text-[#8b949e] text-sm mt-1">{auth.public_repos} repositories · AGA Dashboard</p>
      </div>

      {/* How it works */}
      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-3">📖 How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { label: 'Repo Manager', desc: 'Browse your repos, upload files and deploy them with AI-generated commit messages.', to: '/repo-manager' },
            { label: 'Deep Analyzer', desc: 'Paste any GitHub repo URL to get health scores and an AI architectural report.', to: '/analyzer' },
            { label: 'README Generator', desc: 'Describe your project and generate a professional README in seconds.', to: '/readme' },
            { label: 'Create Repo', desc: 'Instantly create a new GitHub repository without leaving the app.', to: '/create-repo' },
          ].map((item) => (
            <button key={item.to} onClick={() => navigate(item.to)}
              className="text-left bg-[#0d1117] border border-[#30363d] hover:border-[#58a6ff] rounded-lg p-3 transition">
              <div className="text-sm font-semibold text-white mb-1">{item.label}</div>
              <div className="text-xs text-[#8b949e]">{item.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {quickActions.map((a) => (
          <button
            key={a.label}
            onClick={() => navigate(a.to)}
            className="bg-[#161b22] border border-[#21262d] hover:border-[#58a6ff] rounded-xl p-4 text-left transition"
          >
            <div className="text-[#58a6ff] mb-2">{a.icon}</div>
            <div className="text-sm font-semibold">{a.label}</div>
          </button>
        ))}
      </div>

      {/* History */}
      {history.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3">Session History</h2>
          <div className="flex flex-col gap-2">
            {history.map((h, i) => (
              <div key={i} className="bg-[#161b22] border border-[#21262d] rounded-lg px-4 py-2 text-sm flex justify-between">
                <span className="text-[#8b949e]">{h.action}</span>
                <span className="text-[#58a6ff]">{h.detail}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Repos */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Your Repositories</h2>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search repos..."
            className="bg-[#0d1117] border border-[#30363d] text-sm text-white px-3 py-1.5 rounded-md outline-none focus:border-[#58a6ff] w-52"
          />
        </div>
        <div className="flex flex-col gap-2">
          {loading ? (
            <p className="text-[#8b949e] text-sm">Loading repositories...</p>
          ) : filtered.length === 0 ? (
            <p className="text-[#8b949e] text-sm">No repositories found.</p>
          ) : (
            filtered.map((r) => (
              <div key={r.full_name} className="bg-[#161b22] border border-[#21262d] rounded-lg px-4 py-3 flex items-center justify-between hover:border-[#30363d] transition">
                <div>
                  <a href={r.url} target="_blank" rel="noreferrer" className="text-[#58a6ff] text-sm font-medium hover:underline">
                    {r.full_name}
                  </a>
                  {r.description && <p className="text-[#8b949e] text-xs mt-0.5 truncate max-w-sm">{r.description}</p>}
                </div>
                <div className="flex items-center gap-3 text-[#8b949e] text-xs">
                  <span className="flex items-center gap-1"><Star size={12} />{r.stars}</span>
                  {r.private ? <Lock size={12} /> : <Globe size={12} />}
                  <span>{r.updated_at}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  )
}

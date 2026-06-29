import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { authenticate } from '@/lib/api'
import toast from 'react-hot-toast'
import { GitBranch, KeyRound } from 'lucide-react'

export default function Auth() {
  const [token, setToken] = useState('')
  const [groqKey, setGroqKey] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token || !groqKey) return toast.error('Both fields are required')
    setLoading(true)
    try {
      const res = await authenticate(token, groqKey)
      login({ ...res.data, github_token: token, groq_key: groqKey })
      toast.success(`Welcome, ${res.data.name}!`)
      navigate('/dashboard')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      toast.error(error.response?.data?.detail || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0d1117] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <GitBranch size={40} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Sign in to AGA</h1>
          <p className="text-[#8b949e] text-sm mt-1">Enter your credentials to continue</p>
        </div>

        <form onSubmit={handleAuth} className="bg-[#161b22] border border-[#30363d] rounded-xl p-6 flex flex-col gap-4">
          <div>
            <label className="text-sm text-[#8b949e] mb-1 block">GitHub Personal Access Token</label>
            <div className="flex items-center gap-2 bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 focus-within:border-[#58a6ff]">
              <GitBranch size={16} className="text-[#8b949e]" />
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="ghp_..."
                className="bg-transparent text-white text-sm flex-1 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-[#8b949e] mb-1 block">Groq API Key</label>
            <div className="flex items-center gap-2 bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 focus-within:border-[#58a6ff]">
              <KeyRound size={16} className="text-[#8b949e]" />
              <input
                type="password"
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                placeholder="gsk_..."
                className="bg-transparent text-white text-sm flex-1 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-semibold py-2.5 rounded-md transition mt-2"
          >
            {loading ? 'Authenticating...' : 'Authenticate'}
          </button>
        </form>

        <p className="text-center text-[#8b949e] text-xs mt-4">
          Need keys?{' '}
          <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" className="text-[#58a6ff] hover:underline">Groq</a>
          {' · '}
          <a href="https://github.com/settings/tokens" target="_blank" rel="noreferrer" className="text-[#58a6ff] hover:underline">GitHub</a>
        </p>
      </div>
    </div>
  )
}

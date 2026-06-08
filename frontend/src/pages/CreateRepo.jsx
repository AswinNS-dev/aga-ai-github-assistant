import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { createRepo } from '../lib/api'
import toast from 'react-hot-toast'
import { ExternalLink } from 'lucide-react'

export default function CreateRepo() {
  const { auth } = useAuth()
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [isPrivate, setIsPrivate] = useState(true)
  const [loading, setLoading] = useState(false)
  const [created, setCreated] = useState(null)

  const handleCreate = async () => {
    if (!name) return toast.error('Repository name is required')
    setLoading(true)
    try {
      const res = await createRepo({ github_token: auth.github_token, name, description: desc, private: isPrivate })
      setCreated(res.data)
      const history = JSON.parse(sessionStorage.getItem('aga_history') || '[]')
      history.unshift({ action: 'Created repo', detail: res.data.full_name })
      sessionStorage.setItem('aga_history', JSON.stringify(history.slice(0, 10)))
      toast.success(`Repo created: ${res.data.full_name}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Creation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <h1 className="text-2xl font-bold">Create Repository</h1>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-2">📖 How it works</h2>
        <ol className="text-xs text-[#8b949e] flex flex-col gap-1 list-decimal list-inside">
          <li>Enter a name for your new repository</li>
          <li>Add an optional description and choose public or private</li>
          <li>Click <span className="text-white">Create Repository</span> — it'll appear on your GitHub instantly</li>
        </ol>
      </div>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 flex flex-col gap-4">
        <input value={name} onChange={(e) => setName(e.target.value)}
          placeholder="Repository name"
          className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]" />

        <input value={desc} onChange={(e) => setDesc(e.target.value)}
          placeholder="Description (optional)"
          className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]" />

        <label className="flex items-center gap-3 cursor-pointer">
          <div onClick={() => setIsPrivate(!isPrivate)}
            className={`w-10 h-5 rounded-full transition ${isPrivate ? 'bg-[#238636]' : 'bg-[#30363d]'} relative`}>
            <div className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-all ${isPrivate ? 'left-5' : 'left-0.5'}`} />
          </div>
          <span className="text-sm text-[#8b949e]">{isPrivate ? 'Private' : 'Public'} repository</span>
        </label>

        <button onClick={handleCreate} disabled={loading}
          className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-semibold py-2.5 rounded-md transition">
          {loading ? 'Creating...' : 'Create Repository'}
        </button>
      </div>

      {created && (
        <div className="bg-[#161b22] border border-[#238636] rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-green-400 text-sm font-semibold">Repository created!</div>
            <div className="text-[#8b949e] text-xs mt-0.5">{created.full_name}</div>
          </div>
          <a href={created.url} target="_blank" rel="noreferrer"
            className="flex items-center gap-1 text-[#58a6ff] text-xs hover:underline">
            Open <ExternalLink size={12} />
          </a>
        </div>
      )}
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { listRepos, getContents, pushFile } from '../lib/api'
import toast from 'react-hot-toast'
import { Folder, FileCode, ChevronRight, Upload, Trash2 } from 'lucide-react'
import { deleteFile } from '../lib/api'

export default function RepoManager() {
  const { auth } = useAuth()
  const [repos, setRepos] = useState([])
  const [selectedRepo, setSelectedRepo] = useState('')
  const [path, setPath] = useState('')
  const [contents, setContents] = useState([])
  const [targetPath, setTargetPath] = useState('')
  const [content, setContent] = useState('')
  const [commitMsg, setCommitMsg] = useState('')
  const [pushing, setPushing] = useState(false)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    listRepos(auth.github_token, auth.groq_key).then((r) => setRepos(r.data))
  }, [])

  const loadContents = (repo, p = '') => {
    getContents(auth.github_token, repo, p)
      .then((r) => setContents(r.data))
      .catch(() => toast.error('Failed to load contents'))
  }

  const handleRepoChange = (repo) => {
    setSelectedRepo(repo)
    setPath('')
    setTargetPath('')
    setContent('')
    setContents([])
    setCommitMsg('')
    loadContents(repo, '')
  }

  const handleItemClick = (item) => {
    if (item.type === 'dir') {
      setPath(item.path)
      loadContents(selectedRepo, item.path)
    } else {
      setTargetPath(item.path)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      setContent(ev.target.result)
      setTargetPath(path ? `${path}/${file.name}` : file.name)
    }
    reader.readAsText(file)
  }

  const handleDelete = async (item) => {
    if (!confirm(`Delete "${item.path}"?`)) return
    setDeleting(item.path)
    try {
      const res = await deleteFile({ github_token: auth.github_token, repo_name: selectedRepo, file_path: item.path })
      toast.success(res.data.message)
      loadContents(selectedRepo, path)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Delete failed')
    } finally {
      setDeleting(null)
    }
  }

  const handlePush = async () => {
    if (!selectedRepo || !targetPath || !content) return toast.error('Missing repo, path, or content')
    setPushing(true)
    try {
      const res = await pushFile({
        github_token: auth.github_token,
        groq_key: auth.groq_key,
        repo_name: selectedRepo,
        file_path: targetPath,
        content,
        commit_message: commitMsg,
      })
      toast.success(res.data.message)
      const history = JSON.parse(sessionStorage.getItem('aga_history') || '[]')
      history.unshift({ action: 'Pushed file', detail: targetPath })
      sessionStorage.setItem('aga_history', JSON.stringify(history.slice(0, 10)))
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Push failed')
    } finally {
      setPushing(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">Repo Manager</h1>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-2">📖 How it works</h2>
        <ol className="text-xs text-[#8b949e] flex flex-col gap-1 list-decimal list-inside">
          <li>Select a repository from the dropdown to browse its files</li>
          <li>Click a file to select its path, or upload a new file from your computer</li>
          <li>Hit <span className="text-white">Deploy to GitHub</span> — AI will auto-generate a commit message if you leave it blank</li>
          <li>Use the <span className="text-white">🗑 trash icon</span> next to any file to delete it from the repo</li>
        </ol>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left - Explorer */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 flex flex-col gap-4">
          <h2 className="font-semibold text-sm text-[#8b949e]">FILE EXPLORER</h2>
          <select
            value={selectedRepo}
            onChange={(e) => handleRepoChange(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]"
          >
            <option value="">Select a repository</option>
            {repos.map((r) => <option key={r.full_name} value={r.full_name}>{r.full_name}</option>)}
          </select>

          {path && (
            <button onClick={() => { const p = path.split('/').slice(0, -1).join('/'); setPath(p); loadContents(selectedRepo, p) }}
              className="text-xs text-[#58a6ff] hover:underline text-left">
              ← Back
            </button>
          )}

          <div className="flex flex-col gap-1 max-h-64 overflow-y-auto">
            {contents.map((item) => (
              <div key={item.path} className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-[#21262d] text-sm transition">
                <button onClick={() => handleItemClick(item)} className="flex items-center gap-2 flex-1 text-left">
                  {item.type === 'dir' ? <Folder size={15} className="text-[#58a6ff]" /> : <FileCode size={15} className="text-[#8b949e]" />}
                  <span className="truncate">{item.name}</span>
                  {item.type === 'dir' && <ChevronRight size={14} className="ml-auto text-[#8b949e]" />}
                </button>
                <button onClick={() => setTargetPath(item.path)}
                  className="text-xs text-[#8b949e] hover:text-[#58a6ff] border border-[#30363d] hover:border-[#58a6ff] px-2 py-0.5 rounded transition whitespace-nowrap">
                  Select Path
                </button>
                <button onClick={() => handleDelete(item)} disabled={deleting === item.path}
                  className="text-[#f85149] hover:text-red-400 disabled:opacity-40 transition">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Right - Deploy */}
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 flex flex-col gap-4">
          <h2 className="font-semibold text-sm text-[#8b949e]">DEPLOY FILE</h2>

          <label className="flex items-center gap-2 bg-[#0d1117] border border-dashed border-[#30363d] hover:border-[#58a6ff] rounded-md px-4 py-6 cursor-pointer justify-center transition">
            <Upload size={18} className="text-[#58a6ff]" />
            <span className="text-sm text-[#8b949e]">Upload a file</span>
            <input type="file" className="hidden" onChange={handleFileUpload} />
          </label>

          <input value={targetPath} onChange={(e) => setTargetPath(e.target.value)}
            placeholder="Target path (e.g. src/file.py)"
            className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]" />

          <textarea value={content} onChange={(e) => setContent(e.target.value)}
            placeholder="File content..."
            rows={6}
            className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff] resize-none font-mono" />

          <input value={commitMsg} onChange={(e) => setCommitMsg(e.target.value)}
            placeholder="Commit message (leave blank for AI)"
            className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]" />

          <button onClick={handlePush} disabled={pushing}
            className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-semibold py-2.5 rounded-md transition">
            {pushing ? 'Pushing...' : 'Deploy to GitHub'}
          </button>

          <p className="text-xs text-[#8b949e] text-center">⚠️ NOTE: Maximum file size that can be pushed is <span className="text-white font-semibold">25 MB</span></p>
        </div>
      </div>
    </div>
  )
}

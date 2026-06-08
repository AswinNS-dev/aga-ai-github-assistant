import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { analyzeRepo } from '../lib/api'
import toast from 'react-hot-toast'

const models = ['llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768']

export default function Analyzer() {
  const { auth } = useAuth()
  const [url, setUrl] = useState('')
  const [model, setModel] = useState(models[0])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!url) return toast.error('Enter a repository URL')
    setLoading(true)
    try {
      const res = await analyzeRepo({ github_token: auth.github_token, groq_key: auth.groq_key, repo_url: url, model })
      setResult(res.data)
      const history = JSON.parse(sessionStorage.getItem('aga_history') || '[]')
      history.unshift({ action: 'Analyzed repo', detail: url.replace('https://github.com/', '') })
      sessionStorage.setItem('aga_history', JSON.stringify(history.slice(0, 10)))
      toast.success('Analysis complete!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = (s) => s >= 80 ? 'text-green-400' : s >= 50 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <h1 className="text-2xl font-bold">Deep Analyzer</h1>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-2">📖 How it works</h2>
        <ol className="text-xs text-[#8b949e] flex flex-col gap-1 list-decimal list-inside">
          <li>Paste any public or private GitHub repository URL</li>
          <li>Choose an AI model for the analysis</li>
          <li>Hit <span className="text-white">Start Deep Analysis</span> to get health scores and an AI architectural report</li>
        </ol>
      </div>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 flex flex-col gap-4">
        <input value={url} onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/username/repo"
          className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]" />

        <select value={model} onChange={(e) => setModel(e.target.value)}
          className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff]">
          {models.map((m) => <option key={m}>{m}</option>)}
        </select>

        <button onClick={handleAnalyze} disabled={loading}
          className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-semibold py-2.5 rounded-md transition">
          {loading ? 'Analyzing...' : 'Start Deep Analysis'}
        </button>
      </div>

      {result && (
        <div className="flex flex-col gap-4">
          {/* Scores */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(result.scores).map(([key, val]) => (
              <div key={key} className="bg-[#161b22] border border-[#21262d] rounded-xl p-4 text-center">
                <div className={`text-3xl font-bold ${scoreColor(val)}`}>{val}</div>
                <div className="text-xs text-[#8b949e] mt-1 capitalize">{key}</div>
              </div>
            ))}
          </div>

          {/* Report */}
          <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
            <h2 className="font-semibold mb-3 text-sm text-[#8b949e]">AI REPORT</h2>
            <pre className="text-sm text-white whitespace-pre-wrap font-sans">{result.report}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

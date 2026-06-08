import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { generateReadme } from '../lib/api'
import toast from 'react-hot-toast'
import { Copy } from 'lucide-react'

const styles = ['professional', 'open_source', 'startup', 'hackathon', 'minimal']

export default function ReadmeGen() {
  const { auth } = useAuth()
  const [context, setContext] = useState('')
  const [style, setStyle] = useState('professional')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    if (!context) return toast.error('Enter project details')
    setLoading(true)
    try {
      const res = await generateReadme({ groq_key: auth.groq_key, context, style })
      setOutput(res.data.readme)
      toast.success('README generated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Generation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <h1 className="text-2xl font-bold">README Generator</h1>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-2">📖 How it works</h2>
        <ol className="text-xs text-[#8b949e] flex flex-col gap-1 list-decimal list-inside">
          <li>Paste your project description, structure, or tech stack in the text box</li>
          <li>Pick a README style (professional, startup, minimal, etc.)</li>
          <li>Click <span className="text-white">Generate README</span> and copy the output</li>
        </ol>
      </div>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5 flex flex-col gap-4">
        <textarea value={context} onChange={(e) => setContext(e.target.value)}
          placeholder="Paste your project structure, description, or tech stack..."
          rows={6}
          className="bg-[#0d1117] border border-[#30363d] text-white text-sm px-3 py-2 rounded-md outline-none focus:border-[#58a6ff] resize-none" />

        <div className="flex gap-2 flex-wrap">
          {styles.map((s) => (
            <button key={s} onClick={() => setStyle(s)}
              className={`text-xs px-3 py-1.5 rounded-full border transition ${style === s ? 'bg-[#1f6feb] border-[#58a6ff] text-white' : 'border-[#30363d] text-[#8b949e] hover:text-white'}`}>
              {s}
            </button>
          ))}
        </div>

        <button onClick={handleGenerate} disabled={loading}
          className="bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white font-semibold py-2.5 rounded-md transition">
          {loading ? 'Generating...' : 'Generate README'}
        </button>
      </div>

      {output && (
        <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-5">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-semibold text-sm text-[#8b949e]">OUTPUT</h2>
            <button onClick={() => { navigator.clipboard.writeText(output); toast.success('Copied!') }}
              className="flex items-center gap-1 text-xs text-[#8b949e] hover:text-white border border-[#30363d] px-2 py-1 rounded transition">
              <Copy size={12} /> Copy
            </button>
          </div>
          <pre className="text-sm text-white whitespace-pre-wrap font-mono overflow-auto max-h-96">{output}</pre>
        </div>
      )}
    </div>
  )
}

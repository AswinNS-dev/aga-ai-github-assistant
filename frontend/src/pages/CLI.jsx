import toast from 'react-hot-toast'
import { Terminal, Copy } from 'lucide-react'

const commands = [
  {
    cmd: 'pip install aga-ai-github-assistant',
    desc: 'Install the AGA CLI package from PyPI',
  },
  {
    cmd: 'aga push',
    desc: 'Interactively push a file or entire folder to a GitHub repo with an AI-generated commit message. Prompts for your GitHub token, Groq key, repo name, branch, and file/folder path.',
  },
  {
    cmd: 'aga create-repo my-repo --description "My project" --public',
    desc: 'Create a new GitHub repository. Use --public to make it public, omit for private. Reads GITHUB_TOKEN from your .env file.',
  },
  {
    cmd: 'aga analyze https://github.com/username/repo',
    desc: 'Deeply analyze any public or private GitHub repo. Returns health, security, and documentation scores along with an AI architectural report. Reads GITHUB_TOKEN and GROQ_API_KEY from your .env file.',
  },
]

export default function CLI() {
  const copy = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied!')
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <Terminal size={22} className="text-[#58a6ff]" />
        <h1 className="text-2xl font-bold">CLI & pip Package</h1>
      </div>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#58a6ff] mb-2">📖 How it works</h2>
        <ol className="text-xs text-[#8b949e] flex flex-col gap-1 list-decimal list-inside">
          <li>Install the package using pip</li>
          <li>Create a <span className="text-white">.env</span> file with your <span className="text-white">GITHUB_TOKEN</span> and <span className="text-white">GROQ_API_KEY</span></li>
          <li>Run any <span className="text-white">aga</span> command from your terminal</li>
        </ol>
      </div>

      <div className="bg-[#161b22] border border-[#21262d] rounded-xl p-4 flex flex-col gap-2">
        <h2 className="text-sm font-semibold text-[#8b949e] mb-1">.env setup</h2>
        {['GITHUB_TOKEN=ghp_...', 'GROQ_API_KEY=gsk_...'].map((line) => (
          <div key={line} className="flex items-center justify-between bg-[#0d1117] px-3 py-2 rounded-md">
            <code className="text-green-400 text-xs">{line}</code>
            <button onClick={() => copy(line)} className="text-[#8b949e] hover:text-white transition"><Copy size={12} /></button>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        {commands.map((c) => (
          <div key={c.cmd} className="bg-[#161b22] border border-[#21262d] rounded-xl p-4 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <code className="text-green-400 text-xs break-all">{c.cmd}</code>
              <button onClick={() => copy(c.cmd)} className="ml-3 shrink-0 text-[#8b949e] hover:text-white transition"><Copy size={13} /></button>
            </div>
            <p className="text-xs text-[#8b949e]">{c.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

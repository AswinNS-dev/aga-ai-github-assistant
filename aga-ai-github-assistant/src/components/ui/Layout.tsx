import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import {
  GitBranch,
  LayoutDashboard,
  FolderGit2,
  Search,
  FileText,
  Plus,
  LogOut,
  Terminal,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useState, type ReactNode } from 'react'

const links = [
  { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
  { to: '/repo-manager', icon: <FolderGit2 size={18} />, label: 'Repo Manager' },
  { to: '/analyzer', icon: <Search size={18} />, label: 'Deep Analyzer' },
  { to: '/readme', icon: <FileText size={18} />, label: 'README Gen' },
  { to: '/create-repo', icon: <Plus size={18} />, label: 'Create Repo' },
  { to: '/cli', icon: <Terminal size={18} />, label: 'CLI & pip' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const { auth, logout } = useAuth()
  const navigate = useNavigate()
  const [showDropdown, setShowDropdown] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="flex min-h-screen bg-[#0d1117] text-white">
      {/* Sidebar */}
      <aside className="w-56 bg-[#161b22] border-r border-[#21262d] flex flex-col">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-[#21262d]">
          <GitBranch size={20} />
          <span className="font-bold">AGA</span>
        </div>

        {/* User */}
        {auth && (
          <div className="border-b border-[#21262d] relative">
            <div
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-[#21262d] transition"
            >
              <img src={auth.avatar} className="w-8 h-8 rounded-full" alt="avatar" />
              <div className="overflow-hidden">
                <div className="text-sm font-semibold truncate">{auth.name}</div>
                <div className="text-xs text-[#8b949e]">{auth.public_repos} repos</div>
              </div>
            </div>

            {/* Dropdown */}
            {showDropdown && (
              <div className="absolute left-4 right-4 bg-[#1c2128] border border-[#30363d] rounded-lg shadow-xl z-50 overflow-hidden">
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-red-400 hover:bg-[#21262d] transition"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </div>
            )}

            <div className="flex items-center gap-2 px-4 py-2 mb-2">
              <code className="text-[#58a6ff] text-xs flex-1 truncate">
                pip install aga-ai-github-assistant
              </code>
              <button
                onClick={() => {
                  navigator.clipboard.writeText('pip install aga-ai-github-assistant')
                  toast.success('Copied!')
                }}
                className="text-[#8b949e] hover:text-white border border-[#30363d] px-1.5 py-0.5 rounded text-xs transition"
              >
                Copy
              </button>
            </div>
          </div>
        )}

        <nav className="flex-1 px-2 py-3 flex flex-col gap-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition ${
                  isActive
                    ? 'bg-[#1f6feb33] text-[#58a6ff]'
                    : 'text-[#8b949e] hover:text-white hover:bg-[#21262d]'
                }`
              }
            >
              {l.icon}
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}

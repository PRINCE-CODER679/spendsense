import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Receipt, 
  Upload, 
  Wallet, 
  Lightbulb, 
  Bot, 
  Settings,
  LogOut,
  User as UserIcon
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const Sidebar = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/transactions', icon: Receipt, label: 'Transactions' },
    { path: '/upload', icon: Upload, label: 'Upload Statement' },
    { path: '/budgets', icon: Wallet, label: 'Budgets' },
    { path: '/insights', icon: Lightbulb, label: 'Insights' },
    { path: '/assistant', icon: Bot, label: 'AI Assistant' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900 border-r border-slate-800 shadow-xl flex flex-col justify-between z-20">
      <div>
        <div className="p-6 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
              <span className="text-lg font-black text-white">S</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-100 tracking-tight">SpendSense AI</h1>
              <p className="text-xs text-slate-400">Multi-User Finance</p>
            </div>
          </div>
        </div>

        <nav className="mt-4 px-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-150 ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 font-semibold shadow-inner'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* User profile & Logout footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden pr-2">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-slate-200 truncate">
                {user?.full_name || 'SpendSense User'}
              </p>
              <p className="text-[11px] text-slate-400 truncate">
                {user?.email || ''}
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            title="Sign Out"
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors flex-shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

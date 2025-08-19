import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  Activity, 
  Server, 
  DollarSign, 
  Monitor, 
  Wifi,
  WifiOff,
  Settings
} from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  connectionStatus: 'Connecting' | 'Open' | 'Closed' | 'Error'
}

const Layout: React.FC<LayoutProps> = ({ children, connectionStatus }) => {
  const location = useLocation()

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Activity,
      description: 'Overview and real-time monitoring'
    },
    {
      name: 'EC2 Instances',
      href: '/instances',
      icon: Server,
      description: 'EC2 instance monitoring across environments'
    },
    {
      name: 'Cost Analysis',
      href: '/costs',
      icon: DollarSign,
      description: 'Cost breakdown and optimization'
    },
    {
      name: 'Real-time Monitoring',
      href: '/monitoring',
      icon: Monitor,
      description: 'Live alerts and system health'
    }
  ]

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'Open':
        return 'text-green-500'
      case 'Connecting':
        return 'text-yellow-500'
      case 'Closed':
      case 'Error':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getConnectionIcon = () => {
    return connectionStatus === 'Open' ? Wifi : WifiOff
  }

  const ConnectionIcon = getConnectionIcon()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">
                  NiroAgent Dashboard
                </h1>
                <p className="text-sm text-gray-500">
                  Real-time AWS Infrastructure Monitoring
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2" data-testid="connection-status">
                <ConnectionIcon className={`h-5 w-5 ${getConnectionStatusColor()}`} />
                <span className={`text-sm font-medium ${getConnectionStatusColor()}`}>
                  {connectionStatus}
                </span>
              </div>
              
              {/* Settings */}
              <button className="p-2 text-gray-400 hover:text-gray-500 rounded-md hover:bg-gray-100">
                <Settings className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-screen border-r border-gray-200">
          <nav className="p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href || 
                             (item.href === '/dashboard' && location.pathname === '/')
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  data-testid={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                    ${isActive
                      ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <item.icon 
                    className={`
                      mr-3 flex-shrink-0 h-5 w-5
                      ${isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}
                    `}
                  />
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </NavLink>
              )
            })}
          </nav>
          
          {/* Environment Info */}
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Environments
              </h3>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">VF-Dev</span>
                  <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">VF-Staging</span>
                  <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
                    Monitor
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">VF-Production</span>
                  <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                    Critical
                  </span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout

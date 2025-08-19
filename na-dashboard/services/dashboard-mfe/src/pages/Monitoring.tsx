import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Monitor, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Play,
  Pause,
  RefreshCw,
  Bell,
  Activity,
  Zap,
  Clock
} from 'lucide-react'

// Types
interface Alert {
  id: string
  environment: string
  type: 'info' | 'warning' | 'error'
  message: string
  resource: string
  timestamp: string
  resolved: boolean
}

interface MonitoringStatus {
  environments: Record<string, {
    status: 'healthy' | 'warning' | 'error'
    instances: number
    alerts: number
    lastUpdate: string
  }>
  totalInstances: number
  totalAlerts: number
  timestamp: string
}

// API functions
const fetchMonitoringStatus = async (): Promise<MonitoringStatus> => {
  const response = await fetch('/api/monitoring/status')
  if (!response.ok) throw new Error('Failed to fetch monitoring status')
  return response.json()
}

const fetchAlerts = async (environment?: string) => {
  const url = environment ? `/api/monitoring/alerts/${environment}` : '/api/monitoring/alerts'
  const response = await fetch(url)
  if (!response.ok) throw new Error('Failed to fetch alerts')
  return response.json()
}

const startMonitoring = async () => {
  const response = await fetch('/api/monitoring/start', { method: 'POST' })
  if (!response.ok) throw new Error('Failed to start monitoring')
  return response.json()
}

const stopMonitoring = async () => {
  const response = await fetch('/api/monitoring/stop', { method: 'POST' })
  if (!response.ok) throw new Error('Failed to stop monitoring')
  return response.json()
}

const sendTestAlert = async (environment: string, type: string, message: string) => {
  const response = await fetch('/api/monitoring/test-alert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ environment, type, message })
  })
  if (!response.ok) throw new Error('Failed to send test alert')
  return response.json()
}

const Monitoring: React.FC = () => {
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('all')
  const [isMonitoringActive, setIsMonitoringActive] = useState(false)
  const [realTimeUpdates, setRealTimeUpdates] = useState<any[]>([])

  // Fetch monitoring status
  const { 
    data: statusData, 
    isLoading: statusLoading, 
    error: statusError,
    refetch: refetchStatus 
  } = useQuery({
    queryKey: ['monitoring-status'],
    queryFn: fetchMonitoringStatus,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  // Fetch alerts
  const { 
    data: alertsData, 
    isLoading: alertsLoading,
    refetch: refetchAlerts 
  } = useQuery({
    queryKey: ['alerts', selectedEnvironment],
    queryFn: () => fetchAlerts(selectedEnvironment === 'all' ? undefined : selectedEnvironment),
    refetchInterval: 15000, // Refresh every 15 seconds
  })

  // Handle monitoring control
  const handleMonitoringToggle = async () => {
    try {
      if (isMonitoringActive) {
        await stopMonitoring()
        setIsMonitoringActive(false)
      } else {
        await startMonitoring()
        setIsMonitoringActive(true)
      }
    } catch (error) {
      console.error('Failed to toggle monitoring:', error)
    }
  }

  // Handle test alert
  const handleTestAlert = async () => {
    try {
      await sendTestAlert('vf-dev', 'info', 'Test alert from dashboard')
      refetchAlerts()
    } catch (error) {
      console.error('Failed to send test alert:', error)
    }
  }

  // Add real-time update simulation
  useEffect(() => {
    const interval = setInterval(() => {
      const newUpdate = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: Math.random() > 0.7 ? 'alert' : 'status',
        environment: ['vf-dev', 'vf-staging', 'vf-production'][Math.floor(Math.random() * 3)],
        message: Math.random() > 0.5 
          ? 'Instance health check completed successfully'
          : 'CPU utilization threshold exceeded',
        severity: Math.random() > 0.8 ? 'warning' : 'info'
      }
      
      setRealTimeUpdates(prev => [newUpdate, ...prev.slice(0, 9)]) // Keep last 10 updates
    }, 8000) // Every 8 seconds

    return () => clearInterval(interval)
  }, [])

  // Get status color and icon
  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'healthy':
        return { color: 'text-green-600 bg-green-100', icon: CheckCircle, label: 'Healthy' }
      case 'warning':
        return { color: 'text-yellow-600 bg-yellow-100', icon: AlertTriangle, label: 'Warning' }
      case 'error':
        return { color: 'text-red-600 bg-red-100', icon: XCircle, label: 'Error' }
      default:
        return { color: 'text-gray-600 bg-gray-100', icon: Monitor, label: 'Unknown' }
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error': return XCircle
      case 'warning': return AlertTriangle
      case 'info': return CheckCircle
      default: return Bell
    }
  }

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-red-600 bg-red-50 border-red-200'
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  if (statusError) {
    return (
      <div className="text-center py-12">
        <Monitor className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load monitoring data</h3>
        <p className="text-gray-500 mb-4">There was an error fetching monitoring information.</p>
        <button onClick={() => refetchStatus()} className="btn-primary">
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Real-time Monitoring</h1>
          <p className="text-gray-600 mt-1">
            Live system health monitoring and alerts across all environments
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleMonitoringToggle}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
              isMonitoringActive 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isMonitoringActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            <span>{isMonitoringActive ? 'Stop' : 'Start'} Monitoring</span>
          </button>
          <button
            onClick={handleTestAlert}
            className="btn-secondary flex items-center space-x-2"
          >
            <Bell className="h-4 w-4" />
            <span>Test Alert</span>
          </button>
          <button
            onClick={() => { refetchStatus(); refetchAlerts(); }}
            className="btn-secondary flex items-center space-x-2"
            disabled={statusLoading}
          >
            <RefreshCw className={`h-4 w-4 ${statusLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-3xl font-bold text-green-600">
                {statusLoading ? '...' : '98.5%'}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <Activity className="h-4 w-4 mr-1" />
                All systems operational
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Instances</p>
              <p className="text-3xl font-bold text-blue-600">
                {statusLoading ? '...' : statusData?.totalInstances || 0}
              </p>
              <p className="text-sm text-blue-600 flex items-center mt-1">
                <Monitor className="h-4 w-4 mr-1" />
                Being monitored
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Monitor className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-3xl font-bold text-red-600">
                {alertsLoading ? '...' : statusData?.totalAlerts || 0}
              </p>
              <p className="text-sm text-red-600 flex items-center mt-1">
                <AlertTriangle className="h-4 w-4 mr-1" />
                Require attention
              </p>
            </div>
            <div className="bg-red-100 p-3 rounded-full">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monitoring Status</p>
              <p className="text-3xl font-bold text-green-600">
                {isMonitoringActive ? 'ACTIVE' : 'PAUSED'}
              </p>
              <p className="text-sm text-gray-600 flex items-center mt-1">
                <Zap className="h-4 w-4 mr-1" />
                Real-time updates
              </p>
            </div>
            <div className={`p-3 rounded-full ${isMonitoringActive ? 'bg-green-100' : 'bg-gray-100'}`}>
              <Zap className={`h-6 w-6 ${isMonitoringActive ? 'text-green-600' : 'text-gray-400'}`} />
            </div>
          </div>
        </div>
      </div>

      {/* Environment Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {statusData && Object.entries(statusData.environments).map(([envName, envData]) => {
          const status = getStatusDisplay(envData.status)
          const StatusIcon = status.icon
          
          return (
            <div key={envName} className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {envName.replace('vf-', '').toUpperCase()}
                </h3>
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${status.color}`}>
                  <StatusIcon className="h-4 w-4" />
                  <span>{status.label}</span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Instances:</span>
                  <span className="font-bold">{envData.instances}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Alerts:</span>
                  <span className={`font-bold ${envData.alerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {envData.alerts}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Update:</span>
                  <span className="text-sm text-gray-500">
                    {new Date(envData.lastUpdate).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Alerts and Real-time Updates */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
            <select
              value={selectedEnvironment}
              onChange={(e) => setSelectedEnvironment(e.target.value)}
              className="form-select text-sm border-gray-300 rounded-md"
            >
              <option value="all">All Environments</option>
              <option value="vf-dev">VF-Development</option>
              <option value="vf-staging">VF-Staging</option>
              <option value="vf-production">VF-Production</option>
            </select>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alertsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : alertsData?.alerts?.length > 0 ? (
              alertsData.alerts.map((alert: Alert) => {
                const AlertIcon = getAlertIcon(alert.type)
                return (
                  <div 
                    key={alert.id}
                    className={`p-4 rounded-lg border ${getAlertColor(alert.type)}`}
                  >
                    <div className="flex items-start space-x-3">
                      <AlertIcon className="h-5 w-5 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">
                          {alert.message}
                        </p>
                        <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                          <span className="capitalize">{alert.environment.replace('vf-', '')}</span>
                          <span>{alert.resource}</span>
                          <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                        </div>
                      </div>
                      {alert.resolved && (
                        <span className="text-xs text-green-600 font-medium">Resolved</span>
                      )}
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>No alerts found</p>
              </div>
            )}
          </div>
        </div>

        {/* Real-time Updates */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Live Activity Feed</h3>
            <div className={`flex items-center space-x-2 ${isMonitoringActive ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isMonitoringActive ? 'bg-green-600 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-sm font-medium">
                {isMonitoringActive ? 'LIVE' : 'PAUSED'}
              </span>
            </div>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {realTimeUpdates.length > 0 ? (
              realTimeUpdates.map((update) => (
                <div key={update.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`p-1 rounded-full ${
                    update.severity === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <Activity className={`h-3 w-3 ${
                      update.severity === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{update.message}</p>
                    <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                      <span className="capitalize">{update.environment.replace('vf-', '')}</span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {new Date(update.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>No recent activity</p>
                <p className="text-xs mt-1">Start monitoring to see live updates</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Monitoring

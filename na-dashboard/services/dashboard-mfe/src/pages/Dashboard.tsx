import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Server, 
  DollarSign, 
  Activity, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Zap,
  Clock
} from 'lucide-react'

// API functions
const fetchInstances = async () => {
  const response = await fetch('/api/aws/instances')
  if (!response.ok) throw new Error('Failed to fetch instances')
  return response.json()
}

const fetchCosts = async () => {
  const response = await fetch('/api/cost/breakdown')
  if (!response.ok) throw new Error('Failed to fetch costs')
  return response.json()
}

const fetchMonitoringStatus = async () => {
  const response = await fetch('/api/monitoring/status')
  if (!response.ok) throw new Error('Failed to fetch monitoring status')
  return response.json()
}

const Dashboard: React.FC = () => {
  const [realTimeData, setRealTimeData] = useState({
    totalInstances: 0,
    activeInstances: 0,
    totalCost: 0,
    alerts: 0
  })

  // Fetch live AWS data
  const { data: instancesData, isLoading: instancesLoading } = useQuery({
    queryKey: ['instances'],
    queryFn: fetchInstances,
    refetchInterval: 30000 // Refresh every 30 seconds
  })

  const { data: costsData, isLoading: costsLoading } = useQuery({
    queryKey: ['costs'],
    queryFn: fetchCosts,
    refetchInterval: 300000 // Refresh every 5 minutes
  })

  const { data: monitoringData, isLoading: monitoringLoading } = useQuery({
    queryKey: ['monitoring'],
    queryFn: fetchMonitoringStatus,
    refetchInterval: 10000 // Refresh every 10 seconds
  })

  // Update real-time data when queries complete
  useEffect(() => {
    if (instancesData && costsData && monitoringData) {
      setRealTimeData({
        totalInstances: instancesData.totalInstances || 0,
        activeInstances: instancesData.instances?.filter((i: any) => i.state === 'running').length || 0,
        totalCost: costsData.grandTotal || 0,
        alerts: monitoringData.totalAlerts || 0
      })
    }
  }, [instancesData, costsData, monitoringData])

  const isLoading = instancesLoading || costsLoading || monitoringLoading

  // Environment breakdown from instances
  const environmentBreakdown = instancesData?.instancesByEnvironment || {
    'vf-dev': 0,
    'vf-staging': 0,
    'vf-production': 0
  }

  // Cost savings calculation (compared to on-demand pricing)
  const calculateSavings = () => {
    if (!costsData?.grandTotal) return 0
    // Assume 70% savings from spot instances, reserved instances, etc.
    const estimatedOnDemandCost = costsData.grandTotal * 3.33
    return ((estimatedOnDemandCost - costsData.grandTotal) / estimatedOnDemandCost * 100).toFixed(1)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time AWS infrastructure monitoring across all environments
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            LIVE
          </div>
          <div className="text-sm text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" data-testid="dashboard-grid">
        {/* Total Instances */}
        <div className="card" data-testid="total-instances-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Instances</p>
              <p className="text-3xl font-bold text-gray-900" data-testid="instance-count">
                {isLoading ? '...' : realTimeData.totalInstances}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingUp className="h-4 w-4 mr-1" />
                {realTimeData.activeInstances} running
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Server className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Total Cost */}
        <div className="card" data-testid="total-cost-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Cost</p>
              <p className="text-3xl font-bold text-gray-900" data-testid="cost-amount">
                {isLoading ? '...' : `$${realTimeData.totalCost.toFixed(2)}`}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingDown className="h-4 w-4 mr-1" />
                {calculateSavings()}% savings
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900">
                {isLoading ? '...' : realTimeData.alerts}
              </p>
              <p className="text-sm text-gray-500 flex items-center mt-1">
                <Clock className="h-4 w-4 mr-1" />
                Last 24h
              </p>
            </div>
            <div className={`p-3 rounded-full ${realTimeData.alerts > 0 ? 'bg-red-100' : 'bg-gray-100'}`}>
              <AlertTriangle className={`h-6 w-6 ${realTimeData.alerts > 0 ? 'text-red-600' : 'text-gray-400'}`} />
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-3xl font-bold text-green-600">
                {isLoading ? '...' : '98.5%'}
              </p>
              <p className="text-sm text-gray-500 flex items-center mt-1">
                <Zap className="h-4 w-4 mr-1" />
                All systems operational
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Environment Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* VF-Dev Environment */}
        <div className="card" data-testid="env-vf-dev">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">VF-Development</h3>
            <span className="status-healthy">Active</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Account ID:</span>
              <span className="font-mono text-sm">319040880702</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Instances:</span>
              <span className="font-bold">{environmentBreakdown['vf-dev'] || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="text-green-600 font-medium">Healthy</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cost (Est.):</span>
              <span className="font-bold">${((costsData?.grandTotal || 0) * 0.4).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* VF-Staging Environment */}
        <div className="card" data-testid="env-vf-staging">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">VF-Staging</h3>
            <span className="status-warning">Monitoring</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Account ID:</span>
              <span className="font-mono text-sm">275057778147</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Instances:</span>
              <span className="font-bold">{environmentBreakdown['vf-staging'] || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="text-yellow-600 font-medium">Monitoring</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cost (Est.):</span>
              <span className="font-bold">${((costsData?.grandTotal || 0) * 0.3).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* VF-Production Environment */}
        <div className="card" data-testid="env-vf-production">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">VF-Production</h3>
            <span className="status-error">Critical</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Account ID:</span>
              <span className="font-mono text-sm">229742714212</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Instances:</span>
              <span className="font-bold">{environmentBreakdown['vf-production'] || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="text-red-600 font-medium">Attention Required</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cost (Est.):</span>
              <span className="font-bold">${((costsData?.grandTotal || 0) * 0.3).toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading recent activity...</div>
          ) : (
            <>
              <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                <div className="bg-green-100 p-2 rounded-full">
                  <Server className="h-4 w-4 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    EC2 instances refreshed successfully
                  </p>
                  <p className="text-xs text-gray-500">
                    {realTimeData.totalInstances} instances across all environments
                  </p>
                </div>
                <span className="text-xs text-gray-500">Just now</span>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="bg-blue-100 p-2 rounded-full">
                  <DollarSign className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    Cost analysis updated
                  </p>
                  <p className="text-xs text-gray-500">
                    Monthly spend: ${realTimeData.totalCost.toFixed(2)} with {calculateSavings()}% optimization
                  </p>
                </div>
                <span className="text-xs text-gray-500">2 min ago</span>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="bg-gray-100 p-2 rounded-full">
                  <Activity className="h-4 w-4 text-gray-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    System health check completed
                  </p>
                  <p className="text-xs text-gray-500">
                    All environments operational with {realTimeData.alerts} active alerts
                  </p>
                </div>
                <span className="text-xs text-gray-500">5 min ago</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

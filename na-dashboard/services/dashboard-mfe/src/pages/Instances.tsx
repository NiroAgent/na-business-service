import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Server, 
  Power, 
  PowerOff, 
  Pause, 
  Clock,
  DollarSign,
  Monitor,
  Filter,
  RefreshCw
} from 'lucide-react'

// Types
interface EC2Instance {
  instanceId: string
  instanceType: string
  state: string
  launchTime?: string
  publicIpAddress?: string
  privateIpAddress?: string
  tags: Record<string, string>
  environment: string
  accountId: string
}

interface InstancesResponse {
  totalInstances: number
  instancesByEnvironment: Record<string, number>
  instances: EC2Instance[]
  timestamp: string
}

// API function
const fetchInstances = async (): Promise<InstancesResponse> => {
  const response = await fetch('/api/aws/instances')
  if (!response.ok) throw new Error('Failed to fetch instances')
  return response.json()
}

const fetchInstanceMetrics = async (environment: string, instanceId: string) => {
  const response = await fetch(`/api/aws/metrics/${environment}/${instanceId}`)
  if (!response.ok) throw new Error('Failed to fetch metrics')
  return response.json()
}

const Instances: React.FC = () => {
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('all')
  const [selectedInstance, setSelectedInstance] = useState<string | null>(null)

  // Fetch instances data
  const { 
    data: instancesData, 
    isLoading, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['instances'],
    queryFn: fetchInstances,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch metrics for selected instance
  const { data: metricsData } = useQuery({
    queryKey: ['metrics', selectedInstance],
    queryFn: () => {
      if (!selectedInstance || !instancesData) return null
      const instance = instancesData.instances.find(i => i.instanceId === selectedInstance)
      if (!instance) return null
      return fetchInstanceMetrics(instance.environment, selectedInstance)
    },
    enabled: !!selectedInstance,
    refetchInterval: 60000, // Refresh every minute
  })

  // Filter instances by environment
  const filteredInstances = instancesData?.instances.filter(instance => 
    selectedEnvironment === 'all' || instance.environment === selectedEnvironment
  ) || []

  // Get status color and icon
  const getStatusDisplay = (state: string) => {
    switch (state) {
      case 'running':
        return { color: 'text-green-600 bg-green-100', icon: Power, label: 'Running' }
      case 'stopped':
        return { color: 'text-red-600 bg-red-100', icon: PowerOff, label: 'Stopped' }
      case 'stopping':
        return { color: 'text-yellow-600 bg-yellow-100', icon: Pause, label: 'Stopping' }
      case 'pending':
        return { color: 'text-blue-600 bg-blue-100', icon: Clock, label: 'Pending' }
      default:
        return { color: 'text-gray-600 bg-gray-100', icon: Server, label: state }
    }
  }

  // Calculate estimated cost per instance (simplified)
  const getEstimatedMonthlyCost = (instanceType: string) => {
    const costMap: Record<string, number> = {
      't2.micro': 8.50,
      't2.small': 17.00,
      't2.medium': 34.00,
      't3.micro': 7.50,
      't3.small': 15.00,
      't3.medium': 30.00,
      'm5.large': 70.00,
      'm5.xlarge': 140.00,
      'c5.large': 62.00,
      'c5.xlarge': 124.00
    }
    return costMap[instanceType] || 50.00 // Default estimate
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <Server className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load instances</h3>
        <p className="text-gray-500 mb-4">There was an error fetching EC2 instances.</p>
        <button 
          onClick={() => refetch()}
          className="btn-primary"
        >
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
          <h1 className="text-3xl font-bold text-gray-900">EC2 Instances</h1>
          <p className="text-gray-600 mt-1">
            Real-time monitoring of EC2 instances across all environments
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center space-x-2"
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Instances</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : instancesData?.totalInstances || 0}
              </p>
            </div>
            <Server className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-600">
                {filteredInstances.filter(i => i.state === 'running').length}
              </p>
            </div>
            <Power className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Stopped</p>
              <p className="text-2xl font-bold text-red-600">
                {filteredInstances.filter(i => i.state === 'stopped').length}
              </p>
            </div>
            <PowerOff className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Est. Monthly Cost</p>
              <p className="text-2xl font-bold text-gray-900">
                ${filteredInstances
                  .filter(i => i.state === 'running')
                  .reduce((sum, i) => sum + getEstimatedMonthlyCost(i.instanceType), 0)
                  .toFixed(0)}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Environment Filter */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">Environment:</span>
        </div>
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

      {/* Instances Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredInstances.map((instance) => {
            const status = getStatusDisplay(instance.state)
            const StatusIcon = status.icon
            
            return (
              <div 
                key={instance.instanceId}
                className={`card cursor-pointer transition-all hover:shadow-lg ${
                  selectedInstance === instance.instanceId ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedInstance(
                  selectedInstance === instance.instanceId ? null : instance.instanceId
                )}
              >
                {/* Instance Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${status.color}`}>
                      <StatusIcon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {instance.tags.Name || instance.instanceId}
                      </h3>
                      <p className="text-xs text-gray-500 font-mono">
                        {instance.instanceId}
                      </p>
                    </div>
                  </div>
                  <span className={`status-indicator ${status.color.replace('text-', '').replace('bg-', 'bg-').replace('-600', '-100').replace('-100', '-800')}`}>
                    {status.label}
                  </span>
                </div>

                {/* Instance Details */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium">{instance.instanceType}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Environment:</span>
                    <span className="font-medium capitalize">
                      {instance.environment.replace('vf-', '')}
                    </span>
                  </div>

                  {instance.publicIpAddress && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Public IP:</span>
                      <span className="font-mono text-xs">{instance.publicIpAddress}</span>
                    </div>
                  )}

                  {instance.privateIpAddress && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Private IP:</span>
                      <span className="font-mono text-xs">{instance.privateIpAddress}</span>
                    </div>
                  )}

                  <div className="flex justify-between">
                    <span className="text-gray-600">Est. Cost:</span>
                    <span className="font-medium text-green-600">
                      ${getEstimatedMonthlyCost(instance.instanceType)}/mo
                    </span>
                  </div>

                  {instance.launchTime && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Launched:</span>
                      <span className="text-xs">
                        {new Date(instance.launchTime).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Tags */}
                {Object.keys(instance.tags).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(instance.tags)
                        .filter(([key]) => key !== 'Name')
                        .slice(0, 3)
                        .map(([key, value]) => (
                        <span 
                          key={key}
                          className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                        >
                          {key}: {value}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metrics Preview (if selected) */}
                {selectedInstance === instance.instanceId && metricsData && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-2 mb-2">
                      <Monitor className="h-4 w-4 text-gray-600" />
                      <span className="text-sm font-medium text-gray-700">
                        Recent Metrics
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-blue-50 p-2 rounded">
                        <div className="text-blue-600 font-medium">CPU</div>
                        <div className="text-blue-800">
                          {metricsData.metrics.cpu?.datapoints?.[0]?.average?.toFixed(1) || 'N/A'}%
                        </div>
                      </div>
                      <div className="bg-green-50 p-2 rounded">
                        <div className="text-green-600 font-medium">Status</div>
                        <div className="text-green-800">Monitored</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredInstances.length === 0 && (
        <div className="text-center py-12">
          <Server className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No instances found
          </h3>
          <p className="text-gray-500">
            {selectedEnvironment === 'all' 
              ? 'No EC2 instances are currently available in any environment.'
              : `No EC2 instances found in ${selectedEnvironment}.`
            }
          </p>
        </div>
      )}
    </div>
  )
}

export default Instances

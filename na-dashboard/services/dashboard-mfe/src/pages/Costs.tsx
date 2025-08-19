import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  PieChart,
  BarChart3,
  RefreshCw,
  Download
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Cell,
  BarChart,
  Bar
} from 'recharts'

// Types
interface CostData {
  environment?: string
  period: number
  grandTotal: number
  currency: string
  environments: Array<{
    environment: string
    accountId: string
    totalCost: number
    topServices: Array<{
      service: string
      cost: number
    }>
    currency: string
  }>
  timestamp: string
}

// API functions
const fetchCosts = async (): Promise<CostData> => {
  const response = await fetch('/api/cost/breakdown')
  if (!response.ok) throw new Error('Failed to fetch costs')
  return response.json()
}

const fetchCostTrends = async (environment: string) => {
  const response = await fetch(`/api/cost/trends/${environment}?period=30`)
  if (!response.ok) throw new Error('Failed to fetch cost trends')
  return response.json()
}

const Costs: React.FC = () => {
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('vf-dev')
  const [timePeriod, setTimePeriod] = useState<number>(30)

  // Fetch cost data
  const { 
    data: costsData, 
    isLoading: costsLoading, 
    error: costsError,
    refetch 
  } = useQuery({
    queryKey: ['costs'],
    queryFn: fetchCosts,
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  // Fetch trends data
  const { 
    data: trendsData, 
    isLoading: trendsLoading 
  } = useQuery({
    queryKey: ['cost-trends', selectedEnvironment, timePeriod],
    queryFn: () => fetchCostTrends(selectedEnvironment),
    refetchInterval: 300000,
  })

  // Colors for charts
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']

  // Prepare data for charts
  const pieData = costsData?.environments.map((env, index) => ({
    name: env.environment.replace('vf-', '').toUpperCase(),
    value: env.totalCost,
    color: colors[index % colors.length]
  })) || []

  const serviceData = costsData?.environments
    .find(env => env.environment === selectedEnvironment)
    ?.topServices.map((service, index) => ({
      name: service.service.replace('Amazon ', '').replace('AWS ', ''),
      cost: service.cost,
      color: colors[index % colors.length]
    })) || []

  const trendData = trendsData?.trends?.map((point: any) => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    cost: point.cost,
    movingAvg: point.movingAvg
  })) || []

  // Calculate cost optimization metrics
  const calculateOptimization = () => {
    if (!costsData?.grandTotal) return { savings: 0, percentage: 0 }
    
    // Estimate potential savings based on current spend
    const estimatedOptimization = costsData.grandTotal * 0.25 // 25% potential savings
    const percentage = 25
    
    return { savings: estimatedOptimization, percentage }
  }

  const optimization = calculateOptimization()

  if (costsError) {
    return (
      <div className="text-center py-12">
        <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load cost data</h3>
        <p className="text-gray-500 mb-4">There was an error fetching cost information.</p>
        <button onClick={() => refetch()} className="btn-primary">
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
          <h1 className="text-3xl font-bold text-gray-900">Cost Analysis</h1>
          <p className="text-gray-600 mt-1">
            AWS cost breakdown and optimization across all environments
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timePeriod}
            onChange={(e) => setTimePeriod(Number(e.target.value))}
            className="form-select text-sm border-gray-300 rounded-md"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center space-x-2"
            disabled={costsLoading}
          >
            <RefreshCw className={`h-4 w-4 ${costsLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Cost Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Monthly Cost</p>
              <p className="text-3xl font-bold text-gray-900">
                ${costsLoading ? '...' : costsData?.grandTotal.toFixed(2) || '0.00'}
              </p>
              <p className="text-sm text-blue-600 flex items-center mt-1">
                <Calendar className="h-4 w-4 mr-1" />
                Last 30 days
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Potential Savings</p>
              <p className="text-3xl font-bold text-green-600">
                ${optimization.savings.toFixed(2)}
              </p>
              <p className="text-sm text-green-600 flex items-center mt-1">
                <TrendingDown className="h-4 w-4 mr-1" />
                {optimization.percentage}% optimization
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <TrendingDown className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Largest Environment</p>
              <p className="text-3xl font-bold text-gray-900">
                {costsData?.environments.length ? 
                  costsData.environments.reduce((max, env) => 
                    env.totalCost > max.totalCost ? env : max
                  ).environment.replace('vf-', '').toUpperCase() 
                  : 'N/A'
                }
              </p>
              <p className="text-sm text-gray-600 flex items-center mt-1">
                <PieChart className="h-4 w-4 mr-1" />
                By spend
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost Trend</p>
              <p className="text-3xl font-bold text-green-600">
                {trendsData?.trends?.length > 1 ? (
                  trendsData.trends[trendsData.trends.length - 1].cost > 
                  trendsData.trends[trendsData.trends.length - 2].cost ? '↑' : '↓'
                ) : '→'}
              </p>
              <p className="text-sm text-gray-600 flex items-center mt-1">
                <TrendingUp className="h-4 w-4 mr-1" />
                vs last period
              </p>
            </div>
            <div className="bg-orange-100 p-3 rounded-full">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Environment Breakdown and Cost Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Environment Cost Breakdown */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Cost by Environment</h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          
          {costsLoading ? (
            <div className="h-64 bg-gray-100 rounded animate-pulse"></div>
          ) : pieData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <RechartsPieChart data={pieData} cx="50%" cy="50%" outerRadius={80}>
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </RechartsPieChart>
                  <Tooltip formatter={(value: any) => [`$${value.toFixed(2)}`, 'Cost']} />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No cost data available
            </div>
          )}
          
          {/* Legend */}
          <div className="grid grid-cols-3 gap-2 mt-4">
            {pieData.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                ></div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-900 truncate">
                    {item.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    ${item.value.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Trends */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Cost Trends - {selectedEnvironment.replace('vf-', '').toUpperCase()}
            </h3>
            <select
              value={selectedEnvironment}
              onChange={(e) => setSelectedEnvironment(e.target.value)}
              className="form-select text-sm border-gray-300 rounded-md"
            >
              <option value="vf-dev">Development</option>
              <option value="vf-staging">Staging</option>
              <option value="vf-production">Production</option>
            </select>
          </div>
          
          {trendsLoading ? (
            <div className="h-64 bg-gray-100 rounded animate-pulse"></div>
          ) : trendData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value: any) => [`$${value.toFixed(2)}`, 'Cost']} />
                  <Line 
                    type="monotone" 
                    dataKey="cost" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="movingAvg" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No trend data available
            </div>
          )}
        </div>
      </div>

      {/* Service Breakdown */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Top Services - {selectedEnvironment.replace('vf-', '').toUpperCase()}
          </h3>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
        </div>
        
        {costsLoading ? (
          <div className="h-64 bg-gray-100 rounded animate-pulse"></div>
        ) : serviceData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value: any) => [`$${value.toFixed(2)}`, 'Cost']} />
                <Bar dataKey="cost" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No service data available for selected environment
          </div>
        )}
      </div>

      {/* Environment Details Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Environment Details</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Environment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Account ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Monthly Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  % of Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {costsData?.environments.map((env) => (
                <tr key={env.environment} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">
                        {env.environment.replace('vf-', '').toUpperCase()}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 font-mono">{env.accountId}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${env.totalCost.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {env.topServices[0]?.service.replace('Amazon ', '').replace('AWS ', '') || 'N/A'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {((env.totalCost / (costsData?.grandTotal || 1)) * 100).toFixed(1)}%
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Costs

// AWS Account Configuration
export interface AWSAccount {
  accountId: string
  roleArn: string
  region: string
  environment: string
}

// EC2 Instance Types
export interface EC2Instance {
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

export interface InstancesResponse {
  environment?: string
  instanceCount?: number
  totalInstances?: number
  instances: EC2Instance[]
  instancesByEnvironment?: Record<string, number>
  errors?: Array<{ environment: string; error: string }>
  timestamp: string
}

// CloudWatch Metrics
export interface MetricDatapoint {
  timestamp?: string
  average?: number
  maximum?: number
  minimum?: number
  sum?: number
}

export interface InstanceMetrics {
  instanceId: string
  environment: string
  metrics: {
    cpu?: {
      datapoints: MetricDatapoint[]
    }
    memory?: {
      datapoints: MetricDatapoint[]
    }
    network?: {
      datapoints: MetricDatapoint[]
    }
  }
  timestamp: string
}

// Cost Explorer Types
export interface CostService {
  service: string
  cost: number
  currency: string
}

export interface DailyCostBreakdown {
  date?: string
  total: number
  currency: string
  services: CostService[]
}

export interface CostBreakdownResponse {
  environment?: string
  period: number
  totalCost: number
  avgDailyCost?: number
  currency: string
  dailyBreakdown?: DailyCostBreakdown[]
  topServices: CostService[]
  timestamp: string
}

export interface AllCostsResponse {
  period: number
  grandTotal: number
  currency: string
  environments: Array<{
    environment: string
    accountId: string
    totalCost: number
    topServices: CostService[]
    currency: string
  }>
  errors?: Array<{ environment: string; error: string }>
  timestamp: string
}

export interface CostTrendDatapoint {
  date?: string
  cost: number
  currency: string
  movingAvg?: number
}

export interface CostTrendsResponse {
  environment: string
  period: number
  trends: CostTrendDatapoint[]
  totalCost: number
  avgDailyCost: number
  timestamp: string
}

// Monitoring Types
export interface Alert {
  id: string
  environment: string
  type: 'info' | 'warning' | 'error'
  message: string
  resource: string
  timestamp: string
  resolved: boolean
}

export interface AlertsResponse {
  environment: string
  alertCount: number
  alerts: Alert[]
  timestamp: string
}

export interface EnvironmentStatus {
  status: 'healthy' | 'warning' | 'error'
  instances: number
  alerts: number
  lastUpdate: string
}

export interface MonitoringStatus {
  environments: Record<string, EnvironmentStatus>
  totalInstances: number
  totalAlerts: number
  timestamp: string
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'connected' | 'alert' | 'status-update' | 'monitoring-started' | 'monitoring-stopped' | 'subscribed' | 'pong'
  topic?: string
  data?: any
  message?: string
  timestamp: string
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
  timestamp: string
  requestId?: string
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  service: string
  timestamp: string
  version?: string
  environment?: string
  checks?: Record<string, string>
}

// Environment Configuration
export type Environment = 'vf-dev' | 'vf-staging' | 'vf-production'

export const ENVIRONMENTS: Environment[] = ['vf-dev', 'vf-staging', 'vf-production']

export const ENVIRONMENT_LABELS: Record<Environment, string> = {
  'vf-dev': 'Development',
  'vf-staging': 'Staging',
  'vf-production': 'Production'
}

export const ENVIRONMENT_COLORS: Record<Environment, string> = {
  'vf-dev': '#10b981', // green
  'vf-staging': '#f59e0b', // amber
  'vf-production': '#ef4444' // red
}

// Dashboard State Types
export interface DashboardState {
  selectedEnvironment?: Environment
  timeRange: {
    start: Date
    end: Date
    preset: '1h' | '6h' | '24h' | '7d' | '30d' | 'custom'
  }
  refreshInterval: number // milliseconds
  isRealTimeEnabled: boolean
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
  environment?: string
}

export interface ChartSeries {
  name: string
  data: ChartDataPoint[]
  color?: string
}

// Utility Types
export type ConnectionStatus = 'Connecting' | 'Open' | 'Closed' | 'Error'

export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  data?: T
  loading: boolean
  error?: string
  lastFetched?: Date
}

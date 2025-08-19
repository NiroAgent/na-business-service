import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import useWebSocket from 'react-use-websocket'
import toast from 'react-hot-toast'

// Components
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Instances from './pages/Instances'
import Costs from './pages/Costs'
import Monitoring from './pages/Monitoring'

// Types
export interface WebSocketMessage {
  type: string
  data?: any
  timestamp: string
}

function App() {
  const [connectionStatus, setConnectionStatus] = useState<'Connecting' | 'Open' | 'Closed' | 'Error'>('Connecting')

  // WebSocket connection for real-time updates
  const { lastMessage, readyState } = useWebSocket(
    `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`,
    {
      onOpen: () => {
        console.log('WebSocket connected')
        setConnectionStatus('Open')
        toast.success('Connected to real-time updates')
      },
      onClose: () => {
        console.log('WebSocket disconnected')
        setConnectionStatus('Closed')
        toast.error('Disconnected from real-time updates')
      },
      onError: (event) => {
        console.error('WebSocket error:', event)
        setConnectionStatus('Error')
        toast.error('WebSocket connection error')
      },
      shouldReconnect: () => true,
      reconnectAttempts: 5,
      reconnectInterval: 3000,
    }
  )

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const message: WebSocketMessage = JSON.parse(lastMessage.data)
        console.log('Received WebSocket message:', message)

        switch (message.type) {
          case 'connected':
            toast.success('WebSocket connected successfully')
            break
          case 'alert':
            const alert = message.data
            if (alert.type === 'error') {
              toast.error(`Alert: ${alert.message}`)
            } else if (alert.type === 'warning') {
              toast(`Warning: ${alert.message}`, { icon: '⚠️' })
            } else {
              toast.success(`Info: ${alert.message}`)
            }
            break
          case 'status-update':
            // Handle real-time status updates
            console.log('Status update:', message.data)
            break
          case 'monitoring-started':
            toast.success('Real-time monitoring started')
            break
          case 'monitoring-stopped':
            toast('Real-time monitoring stopped', { icon: '⏸️' })
            break
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
  }, [lastMessage])

  // Update connection status based on WebSocket ready state
  useEffect(() => {
    switch (readyState) {
      case 0: // CONNECTING
        setConnectionStatus('Connecting')
        break
      case 1: // OPEN
        setConnectionStatus('Open')
        break
      case 2: // CLOSING
      case 3: // CLOSED
        setConnectionStatus('Closed')
        break
      default:
        setConnectionStatus('Error')
    }
  }, [readyState])

  return (
    <Layout connectionStatus={connectionStatus}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/instances" element={<Instances />} />
        <Route path="/costs" element={<Costs />} />
        <Route path="/monitoring" element={<Monitoring />} />
      </Routes>
    </Layout>
  )
}

export default App

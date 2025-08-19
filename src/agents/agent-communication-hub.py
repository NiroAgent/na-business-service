#!/usr/bin/env python3
"""
Inter-Agent Communication Hub for Coordination and Resource Management
Enables message passing, resource coordination, and workload distribution
"""

import json
import time
import threading
import queue
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple, Callable
from pathlib import Path
import requests
import psutil
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('communication_hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CommunicationHub')

class CommunicationHub:
    """Central hub for inter-agent communication and coordination"""
    
    def __init__(self, dashboard_url: str = "http://localhost:5003"):
        self.dashboard_url = dashboard_url
        self.api_url = f"{dashboard_url}/api/data"
        
        # Agent registry
        self.agent_registry = {}
        self.agent_capabilities = {}
        self.agent_status = {}
        self.agent_workload = defaultdict(float)
        
        # Message queues
        self.message_queue = defaultdict(deque)
        self.broadcast_queue = deque(maxlen=1000)
        self.priority_queue = queue.PriorityQueue()
        
        # Resource management
        self.resource_locks = {}
        self.resource_allocation = defaultdict(dict)
        self.resource_limits = {
            'cpu': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'disk_gb': psutil.disk_usage('/').total / (1024**3),
            'network_mbps': 1000,  # Assumed network bandwidth
            'api_calls_per_minute': 1000
        }
        
        # Coordination state
        self.task_assignments = {}
        self.dependencies = defaultdict(list)
        self.execution_order = []
        
        # Communication patterns
        self.message_handlers = {
            'task_request': self._handle_task_request,
            'resource_request': self._handle_resource_request,
            'status_update': self._handle_status_update,
            'coordination': self._handle_coordination,
            'discovery': self._handle_discovery,
            'heartbeat': self._handle_heartbeat,
            'alert': self._handle_alert,
            'result': self._handle_result
        }
        
        # Metrics
        self.metrics = {
            'total_messages': 0,
            'messages_by_type': defaultdict(int),
            'messages_by_agent': defaultdict(int),
            'resource_conflicts': 0,
            'successful_coordinations': 0,
            'failed_coordinations': 0,
            'avg_response_time': 0,
            'response_times': deque(maxlen=100)
        }
        
        # Start worker threads
        self.running = True
        self.message_processor_thread = None
        self.resource_monitor_thread = None
        self.coordinator_thread = None
    
    def register_agent(self, agent_name: str, capabilities: List[str], 
                      resources: Dict[str, float]) -> Dict[str, Any]:
        """Register an agent with the hub"""
        
        logger.info(f"Registering agent: {agent_name}")
        
        self.agent_registry[agent_name] = {
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now(),
            'capabilities': capabilities,
            'resources': resources,
            'status': 'active',
            'message_count': 0
        }
        
        self.agent_capabilities[agent_name] = set(capabilities)
        self.agent_status[agent_name] = 'idle'
        
        # Initialize resource allocation
        for resource_type, amount in resources.items():
            if resource_type in self.resource_allocation:
                self.resource_allocation[resource_type][agent_name] = {
                    'requested': 0,
                    'allocated': 0,
                    'limit': amount
                }
        
        return {
            'success': True,
            'agent_id': agent_name,
            'message': f"Agent {agent_name} registered successfully"
        }
    
    def unregister_agent(self, agent_name: str) -> Dict[str, Any]:
        """Unregister an agent from the hub"""
        
        if agent_name not in self.agent_registry:
            return {
                'success': False,
                'message': f"Agent {agent_name} not found"
            }
        
        # Release resources
        for resource_type in self.resource_allocation:
            if agent_name in self.resource_allocation[resource_type]:
                del self.resource_allocation[resource_type][agent_name]
        
        # Clear message queues
        if agent_name in self.message_queue:
            del self.message_queue[agent_name]
        
        # Remove from registry
        del self.agent_registry[agent_name]
        del self.agent_capabilities[agent_name]
        del self.agent_status[agent_name]
        
        logger.info(f"Unregistered agent: {agent_name}")
        
        return {
            'success': True,
            'message': f"Agent {agent_name} unregistered successfully"
        }
    
    def send_message(self, from_agent: str, to_agent: str, 
                    message_type: str, payload: Any, priority: int = 5) -> Dict[str, Any]:
        """Send a message from one agent to another"""
        
        message = {
            'id': f"{from_agent}_{to_agent}_{datetime.now().timestamp()}",
            'from': from_agent,
            'to': to_agent,
            'type': message_type,
            'payload': payload,
            'timestamp': datetime.now().isoformat(),
            'priority': priority
        }
        
        # Validate agents
        if to_agent not in self.agent_registry and to_agent != 'broadcast':
            return {
                'success': False,
                'message': f"Target agent {to_agent} not registered"
            }
        
        # Route message
        if to_agent == 'broadcast':
            self.broadcast_queue.append(message)
            logger.info(f"Broadcast message from {from_agent}: {message_type}")
        else:
            self.message_queue[to_agent].append(message)
            logger.info(f"Message from {from_agent} to {to_agent}: {message_type}")
        
        # Add to priority queue for processing
        self.priority_queue.put((priority, message))
        
        # Update metrics
        self.metrics['total_messages'] += 1
        self.metrics['messages_by_type'][message_type] += 1
        self.metrics['messages_by_agent'][from_agent] += 1
        
        return {
            'success': True,
            'message_id': message['id'],
            'queued': True
        }
    
    def receive_messages(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Receive pending messages for an agent"""
        
        messages = []
        agent_queue = self.message_queue[agent_name]
        
        # Get direct messages
        for _ in range(min(limit, len(agent_queue))):
            if agent_queue:
                messages.append(agent_queue.popleft())
        
        # Get broadcast messages
        for msg in list(self.broadcast_queue)[-5:]:  # Last 5 broadcasts
            if msg['timestamp'] > self.agent_registry[agent_name].get('last_message_check', ''):
                messages.append(msg)
        
        # Update last check time
        if agent_name in self.agent_registry:
            self.agent_registry[agent_name]['last_message_check'] = datetime.now().isoformat()
        
        return messages
    
    def coordinate_resources(self, requesting_agent: str, resource_type: str, 
                           amount: float, duration_seconds: int = 60) -> Dict[str, Any]:
        """Coordinate resource allocation between agents"""
        
        logger.info(f"{requesting_agent} requesting {amount} {resource_type} for {duration_seconds}s")
        
        # Check if resource type is managed
        if resource_type not in self.resource_limits:
            return {
                'success': False,
                'message': f"Resource type {resource_type} not managed"
            }
        
        # Check availability
        total_allocated = sum(
            alloc.get('allocated', 0) 
            for alloc in self.resource_allocation[resource_type].values()
        )
        available = self.resource_limits[resource_type] - total_allocated
        
        if amount > available:
            # Try to negotiate with other agents
            negotiation_result = self._negotiate_resources(
                requesting_agent, resource_type, amount, available
            )
            
            if not negotiation_result['success']:
                self.metrics['resource_conflicts'] += 1
                return negotiation_result
        
        # Allocate resource
        lock_id = f"{requesting_agent}_{resource_type}_{datetime.now().timestamp()}"
        self.resource_locks[lock_id] = {
            'agent': requesting_agent,
            'resource': resource_type,
            'amount': amount,
            'expires': datetime.now() + timedelta(seconds=duration_seconds)
        }
        
        if requesting_agent not in self.resource_allocation[resource_type]:
            self.resource_allocation[resource_type][requesting_agent] = {
                'requested': 0,
                'allocated': 0
            }
        
        self.resource_allocation[resource_type][requesting_agent]['allocated'] += amount
        
        logger.info(f"Allocated {amount} {resource_type} to {requesting_agent}")
        
        return {
            'success': True,
            'lock_id': lock_id,
            'allocated': amount,
            'expires_in': duration_seconds
        }
    
    def release_resources(self, lock_id: str) -> Dict[str, Any]:
        """Release previously allocated resources"""
        
        if lock_id not in self.resource_locks:
            return {
                'success': False,
                'message': f"Lock {lock_id} not found"
            }
        
        lock = self.resource_locks[lock_id]
        agent = lock['agent']
        resource_type = lock['resource']
        amount = lock['amount']
        
        # Release the resource
        if agent in self.resource_allocation[resource_type]:
            self.resource_allocation[resource_type][agent]['allocated'] -= amount
            self.resource_allocation[resource_type][agent]['allocated'] = max(
                0, self.resource_allocation[resource_type][agent]['allocated']
            )
        
        del self.resource_locks[lock_id]
        
        logger.info(f"Released {amount} {resource_type} from {agent}")
        
        return {
            'success': True,
            'message': f"Released {amount} {resource_type}"
        }
    
    def _negotiate_resources(self, requesting_agent: str, resource_type: str, 
                            requested: float, available: float) -> Dict[str, Any]:
        """Negotiate resource allocation with other agents"""
        
        logger.info(f"Negotiating {resource_type} for {requesting_agent}")
        
        # Find agents with allocated resources
        allocations = self.resource_allocation[resource_type]
        candidates = []
        
        for agent, alloc in allocations.items():
            if agent != requesting_agent and alloc['allocated'] > 0:
                # Check if agent is idle or low priority
                if self.agent_status.get(agent) == 'idle':
                    candidates.append((agent, alloc['allocated'], 'idle'))
                elif self.agent_workload[agent] < 0.3:  # Low workload
                    candidates.append((agent, alloc['allocated'], 'low_workload'))
        
        # Try to reclaim resources from idle/low-priority agents
        reclaimed = 0
        for agent, allocated, reason in candidates:
            if reclaimed >= (requested - available):
                break
            
            # Send negotiation request
            self.send_message(
                'hub', agent, 'resource_negotiation',
                {
                    'resource_type': resource_type,
                    'requested_by': requesting_agent,
                    'amount_needed': requested - available - reclaimed,
                    'reason': f"Higher priority task requires {resource_type}"
                },
                priority=2
            )
            
            # For simulation, assume partial success
            reclaim_amount = min(allocated * 0.5, requested - available - reclaimed)
            allocations[agent]['allocated'] -= reclaim_amount
            reclaimed += reclaim_amount
            
            logger.info(f"Reclaimed {reclaim_amount} {resource_type} from {agent} ({reason})")
        
        if reclaimed + available >= requested:
            return {
                'success': True,
                'message': f"Negotiated {reclaimed} {resource_type} from other agents"
            }
        else:
            return {
                'success': False,
                'message': f"Could not negotiate enough {resource_type}. Available: {available + reclaimed}, Requested: {requested}"
            }
    
    def distribute_workload(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute workload based on agent capacity and capabilities"""
        
        task_type = task.get('type', 'general')
        required_capabilities = task.get('required_capabilities', [])
        estimated_load = task.get('estimated_load', 1.0)
        
        # Find capable agents
        capable_agents = []
        for agent, capabilities in self.agent_capabilities.items():
            if all(cap in capabilities for cap in required_capabilities):
                if self.agent_status.get(agent) != 'offline':
                    capable_agents.append(agent)
        
        if not capable_agents:
            return {
                'success': False,
                'message': f"No agents with required capabilities: {required_capabilities}"
            }
        
        # Select agent with lowest workload
        best_agent = None
        min_workload = float('inf')
        
        for agent in capable_agents:
            current_workload = self.agent_workload[agent]
            if current_workload < min_workload:
                min_workload = current_workload
                best_agent = agent
        
        if best_agent:
            # Assign task
            task_id = f"task_{datetime.now().timestamp()}"
            self.task_assignments[task_id] = {
                'task': task,
                'assigned_to': best_agent,
                'assigned_at': datetime.now().isoformat(),
                'status': 'assigned'
            }
            
            # Update workload
            self.agent_workload[best_agent] += estimated_load
            
            # Send task to agent
            self.send_message(
                'hub', best_agent, 'task_assignment',
                {
                    'task_id': task_id,
                    'task': task
                },
                priority=3
            )
            
            logger.info(f"Assigned task {task_id} to {best_agent} (workload: {min_workload})")
            
            return {
                'success': True,
                'task_id': task_id,
                'assigned_to': best_agent
            }
        
        return {
            'success': False,
            'message': "No suitable agent available"
        }
    
    def manage_dependencies(self, agent_name: str, depends_on: List[str]) -> Dict[str, Any]:
        """Manage execution dependencies between agents"""
        
        self.dependencies[agent_name] = depends_on
        
        # Build execution order using topological sort
        self._update_execution_order()
        
        return {
            'success': True,
            'message': f"Dependencies registered for {agent_name}",
            'execution_order': self.execution_order
        }
    
    def _update_execution_order(self):
        """Update execution order based on dependencies (topological sort)"""
        
        # Build graph
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        
        all_agents = set(self.agent_registry.keys())
        
        for agent, deps in self.dependencies.items():
            for dep in deps:
                graph[dep].append(agent)
                in_degree[agent] += 1
        
        # Add agents with no dependencies
        queue = deque([agent for agent in all_agents if in_degree[agent] == 0])
        self.execution_order = []
        
        while queue:
            agent = queue.popleft()
            self.execution_order.append(agent)
            
            for dependent in graph[agent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        logger.info(f"Updated execution order: {self.execution_order}")
    
    def _handle_task_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task request messages"""
        task = message['payload']
        result = self.distribute_workload(task)
        
        # Send response
        self.send_message(
            'hub', message['from'], 'task_response',
            result, priority=3
        )
        
        return result
    
    def _handle_resource_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource request messages"""
        payload = message['payload']
        result = self.coordinate_resources(
            message['from'],
            payload['resource_type'],
            payload['amount'],
            payload.get('duration', 60)
        )
        
        # Send response
        self.send_message(
            'hub', message['from'], 'resource_response',
            result, priority=2
        )
        
        return result
    
    def _handle_status_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status update messages"""
        agent = message['from']
        status = message['payload']
        
        if agent in self.agent_status:
            self.agent_status[agent] = status.get('status', 'unknown')
            self.agent_workload[agent] = status.get('workload', 0)
            self.agent_registry[agent]['last_seen'] = datetime.now()
        
        return {'success': True, 'message': 'Status updated'}
    
    def _handle_coordination(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle coordination messages between agents"""
        coordination_type = message['payload'].get('type')
        
        if coordination_type == 'sync':
            # Synchronization request
            agents = message['payload'].get('agents', [])
            sync_point = message['payload'].get('sync_point')
            
            # Track sync status
            sync_id = f"sync_{datetime.now().timestamp()}"
            
            # Notify all agents
            for agent in agents:
                if agent != message['from']:
                    self.send_message(
                        'hub', agent, 'sync_request',
                        {'sync_id': sync_id, 'sync_point': sync_point},
                        priority=1
                    )
            
            return {'success': True, 'sync_id': sync_id}
        
        elif coordination_type == 'barrier':
            # Barrier coordination
            barrier_id = message['payload'].get('barrier_id')
            # Implementation for barrier synchronization
            return {'success': True, 'barrier_id': barrier_id}
        
        return {'success': False, 'message': 'Unknown coordination type'}
    
    def _handle_discovery(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service discovery messages"""
        query = message['payload']
        capability = query.get('capability')
        
        # Find agents with requested capability
        matching_agents = [
            agent for agent, caps in self.agent_capabilities.items()
            if capability in caps and self.agent_status.get(agent) != 'offline'
        ]
        
        return {
            'success': True,
            'agents': matching_agents,
            'capability': capability
        }
    
    def _handle_heartbeat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle heartbeat messages"""
        agent = message['from']
        
        if agent in self.agent_registry:
            self.agent_registry[agent]['last_seen'] = datetime.now()
            
            # Check for expired resource locks
            self._cleanup_expired_locks()
        
        return {'success': True, 'message': 'Heartbeat received'}
    
    def _handle_alert(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle alert messages"""
        alert = message['payload']
        severity = alert.get('severity', 'info')
        
        logger.warning(f"Alert from {message['from']}: {alert.get('message')} (Severity: {severity})")
        
        # Broadcast critical alerts
        if severity in ['critical', 'high']:
            self.send_message(
                message['from'], 'broadcast', 'alert_broadcast',
                alert, priority=1
            )
        
        return {'success': True, 'message': 'Alert processed'}
    
    def _handle_result(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task result messages"""
        result = message['payload']
        task_id = result.get('task_id')
        
        if task_id in self.task_assignments:
            self.task_assignments[task_id]['status'] = 'completed'
            self.task_assignments[task_id]['result'] = result
            
            # Update workload
            agent = self.task_assignments[task_id]['assigned_to']
            task_load = self.task_assignments[task_id]['task'].get('estimated_load', 1.0)
            self.agent_workload[agent] = max(0, self.agent_workload[agent] - task_load)
        
        return {'success': True, 'message': 'Result recorded'}
    
    def _cleanup_expired_locks(self):
        """Clean up expired resource locks"""
        current_time = datetime.now()
        expired_locks = []
        
        for lock_id, lock in self.resource_locks.items():
            if lock['expires'] < current_time:
                expired_locks.append(lock_id)
        
        for lock_id in expired_locks:
            self.release_resources(lock_id)
            logger.info(f"Released expired lock: {lock_id}")
    
    def process_messages(self):
        """Process messages from the priority queue"""
        logger.info("Starting message processor...")
        
        while self.running:
            try:
                # Get message from priority queue
                priority, message = self.priority_queue.get(timeout=1)
                
                start_time = datetime.now()
                
                # Process based on message type
                message_type = message['type']
                if message_type in self.message_handlers:
                    result = self.message_handlers[message_type](message)
                    logger.debug(f"Processed {message_type} message: {result}")
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                
                # Track response time
                response_time = (datetime.now() - start_time).total_seconds()
                self.metrics['response_times'].append(response_time)
                
                if self.metrics['response_times']:
                    self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def monitor_resources(self):
        """Monitor and manage resource allocation"""
        logger.info("Starting resource monitor...")
        
        while self.running:
            try:
                # Update system resource limits
                self.resource_limits['cpu'] = psutil.cpu_count()
                self.resource_limits['memory_gb'] = psutil.virtual_memory().available / (1024**3)
                
                # Clean up expired locks
                self._cleanup_expired_locks()
                
                # Check for offline agents
                current_time = datetime.now()
                for agent, data in self.agent_registry.items():
                    last_seen = data.get('last_seen', current_time)
                    if isinstance(last_seen, str):
                        last_seen = datetime.fromisoformat(last_seen)
                    
                    if (current_time - last_seen).total_seconds() > 60:
                        if self.agent_status.get(agent) != 'offline':
                            logger.warning(f"Agent {agent} appears offline")
                            self.agent_status[agent] = 'offline'
                            
                            # Release resources
                            for resource_type in self.resource_allocation:
                                if agent in self.resource_allocation[resource_type]:
                                    self.resource_allocation[resource_type][agent]['allocated'] = 0
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")
    
    def coordinate_agents(self):
        """Main coordination loop"""
        logger.info("Starting agent coordinator...")
        
        while self.running:
            try:
                # Update execution order if dependencies changed
                if self.dependencies:
                    self._update_execution_order()
                
                # Check for coordination opportunities
                idle_agents = [
                    agent for agent, status in self.agent_status.items()
                    if status == 'idle' and self.agent_workload[agent] < 0.1
                ]
                
                # Try to assign pending tasks to idle agents
                for task_id, assignment in self.task_assignments.items():
                    if assignment['status'] == 'pending' and idle_agents:
                        agent = idle_agents.pop(0)
                        assignment['assigned_to'] = agent
                        assignment['status'] = 'assigned'
                        
                        self.send_message(
                            'hub', agent, 'task_assignment',
                            {'task_id': task_id, 'task': assignment['task']},
                            priority=3
                        )
                        
                        self.metrics['successful_coordinations'] += 1
                
                time.sleep(5)  # Coordinate every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in coordinator: {e}")
                self.metrics['failed_coordinations'] += 1
    
    def start(self):
        """Start all hub services"""
        logger.info("Starting Communication Hub...")
        
        # Start worker threads
        self.message_processor_thread = threading.Thread(target=self.process_messages, daemon=True)
        self.resource_monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.coordinator_thread = threading.Thread(target=self.coordinate_agents, daemon=True)
        
        self.message_processor_thread.start()
        self.resource_monitor_thread.start()
        self.coordinator_thread.start()
        
        logger.info("Communication Hub started successfully")
    
    def stop(self):
        """Stop all hub services"""
        logger.info("Stopping Communication Hub...")
        self.running = False
        
        # Wait for threads to finish
        if self.message_processor_thread:
            self.message_processor_thread.join(timeout=5)
        if self.resource_monitor_thread:
            self.resource_monitor_thread.join(timeout=5)
        if self.coordinator_thread:
            self.coordinator_thread.join(timeout=5)
        
        logger.info("Communication Hub stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current hub metrics"""
        return {
            'total_messages': self.metrics['total_messages'],
            'messages_by_type': dict(self.metrics['messages_by_type']),
            'messages_by_agent': dict(self.metrics['messages_by_agent']),
            'resource_conflicts': self.metrics['resource_conflicts'],
            'successful_coordinations': self.metrics['successful_coordinations'],
            'failed_coordinations': self.metrics['failed_coordinations'],
            'avg_response_time': self.metrics['avg_response_time'],
            'active_agents': len([a for a, s in self.agent_status.items() if s != 'offline']),
            'total_agents': len(self.agent_registry),
            'active_tasks': len([t for t in self.task_assignments.values() if t['status'] == 'assigned']),
            'resource_utilization': self._calculate_resource_utilization()
        }
    
    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization percentages"""
        utilization = {}
        
        for resource_type, limit in self.resource_limits.items():
            if resource_type in self.resource_allocation:
                total_allocated = sum(
                    alloc.get('allocated', 0)
                    for alloc in self.resource_allocation[resource_type].values()
                )
                utilization[resource_type] = (total_allocated / limit * 100) if limit > 0 else 0
            else:
                utilization[resource_type] = 0
        
        return utilization
    
    def save_progress(self):
        """Save progress to JSON file"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'component': 'agent-communication-hub',
            'status': 'operational',
            'metrics': self.get_metrics(),
            'registered_agents': list(self.agent_registry.keys()),
            'execution_order': self.execution_order,
            'active_locks': len(self.resource_locks)
        }
        
        # Update existing progress file
        try:
            with open('claude_opus_progress.json', 'r') as f:
                all_progress = json.load(f)
        except:
            all_progress = {}
        
        all_progress['communication_hub'] = progress
        
        with open('claude_opus_progress.json', 'w') as f:
            json.dump(all_progress, f, indent=2)
        
        logger.info("Progress saved to claude_opus_progress.json")


# Example agent client class
class AgentClient:
    """Client for agents to interact with the hub"""
    
    def __init__(self, agent_name: str, hub: CommunicationHub):
        self.agent_name = agent_name
        self.hub = hub
    
    def register(self, capabilities: List[str], resources: Dict[str, float]):
        """Register with the hub"""
        return self.hub.register_agent(self.agent_name, capabilities, resources)
    
    def send(self, to_agent: str, message_type: str, payload: Any, priority: int = 5):
        """Send message to another agent"""
        return self.hub.send_message(self.agent_name, to_agent, message_type, payload, priority)
    
    def receive(self, limit: int = 10):
        """Receive pending messages"""
        return self.hub.receive_messages(self.agent_name, limit)
    
    def request_resource(self, resource_type: str, amount: float, duration: int = 60):
        """Request resource allocation"""
        return self.hub.coordinate_resources(self.agent_name, resource_type, amount, duration)
    
    def update_status(self, status: str, workload: float = 0):
        """Update agent status"""
        return self.hub.send_message(
            self.agent_name, 'hub', 'status_update',
            {'status': status, 'workload': workload}
        )
    
    def heartbeat(self):
        """Send heartbeat to hub"""
        return self.hub.send_message(self.agent_name, 'hub', 'heartbeat', {})


def main():
    """Main execution function"""
    logger.info("Starting Inter-Agent Communication Hub...")
    
    # Initialize hub
    hub = CommunicationHub()
    
    # Start hub services
    hub.start()
    
    # Example: Register some test agents
    test_agents = [
        ('detector_agent', ['monitoring', 'analysis'], {'cpu': 2, 'memory_gb': 1}),
        ('healer_agent', ['healing', 'recovery'], {'cpu': 2, 'memory_gb': 2}),
        ('coordinator_agent', ['coordination', 'scheduling'], {'cpu': 1, 'memory_gb': 0.5})
    ]
    
    for agent_name, capabilities, resources in test_agents:
        hub.register_agent(agent_name, capabilities, resources)
        logger.info(f"Registered test agent: {agent_name}")
    
    try:
        # Keep running and periodically save progress
        while True:
            time.sleep(30)  # Save progress every 30 seconds
            hub.save_progress()
            
            # Log current metrics
            metrics = hub.get_metrics()
            logger.info(f"Hub metrics: {metrics['total_messages']} messages, "
                       f"{metrics['active_agents']}/{metrics['total_agents']} agents active")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        hub.stop()
        hub.save_progress()
        sys.exit(0)


if __name__ == "__main__":
    main()
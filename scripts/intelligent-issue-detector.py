#!/usr/bin/env python3
"""
Intelligent Issue Detection System for Agent Orchestration
Monitors agent outputs and detects failure patterns in real-time
"""

import json
import re
import time
import requests
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import threading
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('issue_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('IssueDetector')

class IssueDetector:
    """Intelligent issue detection system for monitoring agent failures"""
    
    def __init__(self, dashboard_url: str = "http://localhost:5003"):
        self.dashboard_url = dashboard_url
        self.api_url = f"{dashboard_url}/api/data"
        
        # Failure patterns with severity levels
        self.failure_patterns = {
            'network': {
                'patterns': [
                    r'connection.*timeout',
                    r'dns.*error',
                    r'network.*unreachable',
                    r'connection.*refused',
                    r'socket.*error',
                    r'ECONNRESET',
                    r'ETIMEDOUT',
                    r'getaddrinfo.*failed'
                ],
                'severity': 'HIGH',
                'category': 'Infrastructure'
            },
            'auth': {
                'patterns': [
                    r'401.*unauthorized',
                    r'403.*forbidden',
                    r'token.*expired',
                    r'authentication.*failed',
                    r'invalid.*credentials',
                    r'access.*denied',
                    r'permission.*denied',
                    r'not.*authorized'
                ],
                'severity': 'CRITICAL',
                'category': 'Security'
            },
            'rate_limit': {
                'patterns': [
                    r'429.*too many requests',
                    r'quota.*exceeded',
                    r'rate.*limit',
                    r'throttl',
                    r'too.*many.*requests',
                    r'api.*limit',
                    r'exceeded.*limit'
                ],
                'severity': 'MEDIUM',
                'category': 'API'
            },
            'resource': {
                'patterns': [
                    r'out of memory',
                    r'disk.*full',
                    r'cpu.*overload',
                    r'memory.*error',
                    r'insufficient.*resources',
                    r'cannot allocate',
                    r'no space left',
                    r'resource.*exhausted'
                ],
                'severity': 'CRITICAL',
                'category': 'System'
            },
            'crash': {
                'patterns': [
                    r'segmentation fault',
                    r'traceback',
                    r'exception.*unhandled',
                    r'fatal error',
                    r'core dumped',
                    r'process.*terminated',
                    r'unexpected.*exit',
                    r'crash.*detected'
                ],
                'severity': 'CRITICAL',
                'category': 'Stability'
            },
            'copilot': {
                'patterns': [
                    r'copilot.*error',
                    r'subscription.*expired',
                    r'copilot.*unavailable',
                    r'github.*copilot.*failed',
                    r'copilot.*timeout',
                    r'copilot.*permission'
                ],
                'severity': 'HIGH',
                'category': 'Copilot'
            },
            'performance': {
                'patterns': [
                    r'slow.*response',
                    r'high.*latency',
                    r'performance.*degraded',
                    r'timeout.*exceeded',
                    r'response.*time.*high',
                    r'processing.*delayed'
                ],
                'severity': 'MEDIUM',
                'category': 'Performance'
            }
        }
        
        # Issue history for pattern analysis
        self.issue_history = defaultdict(lambda: deque(maxlen=100))
        self.agent_states = {}
        self.resolution_plans = {}
        
        # Metrics tracking
        self.metrics = {
            'total_issues_detected': 0,
            'issues_by_type': defaultdict(int),
            'issues_by_agent': defaultdict(int),
            'detection_times': [],
            'false_positives': 0
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = None
        
    def analyze_agent_output(self, agent_name: str, output: str) -> List[Dict[str, Any]]:
        """
        Analyze agent output for failure patterns
        Returns list of detected issues with details
        """
        detected_issues = []
        output_lower = output.lower()
        
        for issue_type, config in self.failure_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, output_lower, re.IGNORECASE):
                    issue = {
                        'timestamp': datetime.now().isoformat(),
                        'agent_name': agent_name,
                        'issue_type': issue_type,
                        'severity': config['severity'],
                        'category': config['category'],
                        'pattern_matched': pattern,
                        'context': self._extract_context(output, pattern),
                        'confidence': self._calculate_confidence(agent_name, issue_type, output)
                    }
                    
                    detected_issues.append(issue)
                    self._record_issue(agent_name, issue)
                    
                    logger.warning(f"Issue detected for {agent_name}: {issue_type} (Severity: {config['severity']})")
                    break  # Only match first pattern per type
        
        return detected_issues
    
    def _extract_context(self, output: str, pattern: str, context_lines: int = 3) -> str:
        """Extract contextual lines around the matched pattern"""
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                return '\n'.join(lines[start:end])
        return output[:500]  # Return first 500 chars if pattern not found
    
    def _calculate_confidence(self, agent_name: str, issue_type: str, output: str) -> float:
        """Calculate confidence score for detected issue"""
        confidence = 0.7  # Base confidence
        
        # Check if issue is recurring
        history = self.issue_history[agent_name]
        recent_issues = [i for i in history if i['issue_type'] == issue_type]
        if len(recent_issues) > 2:
            confidence += 0.2
        
        # Check for multiple pattern matches
        patterns = self.failure_patterns[issue_type]['patterns']
        matches = sum(1 for p in patterns if re.search(p, output.lower()))
        if matches > 1:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _record_issue(self, agent_name: str, issue: Dict[str, Any]):
        """Record issue in history and update metrics"""
        self.issue_history[agent_name].append(issue)
        self.metrics['total_issues_detected'] += 1
        self.metrics['issues_by_type'][issue['issue_type']] += 1
        self.metrics['issues_by_agent'][agent_name] += 1
        self.metrics['detection_times'].append(datetime.now())
    
    def generate_resolution_plan(self, issue_type: str, agent_name: str, 
                                context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate specific resolution plan for detected issue"""
        
        resolution_plans = {
            'network': {
                'immediate_actions': [
                    'Check network connectivity',
                    'Verify DNS resolution',
                    'Test endpoint availability'
                ],
                'recovery_steps': [
                    'Retry with exponential backoff',
                    'Switch to backup endpoint if available',
                    'Clear DNS cache',
                    'Reset network adapter if persistent'
                ],
                'preventive_measures': [
                    'Implement connection pooling',
                    'Add retry logic with circuit breaker',
                    'Configure timeout values appropriately'
                ]
            },
            'auth': {
                'immediate_actions': [
                    'Verify credential validity',
                    'Check token expiration',
                    'Validate permission scope'
                ],
                'recovery_steps': [
                    'Refresh authentication token',
                    'Re-authenticate with stored credentials',
                    'Request new API key if expired',
                    'Update credential store'
                ],
                'preventive_measures': [
                    'Implement token refresh before expiry',
                    'Add credential rotation schedule',
                    'Monitor auth failures proactively'
                ]
            },
            'rate_limit': {
                'immediate_actions': [
                    'Check current rate limit status',
                    'Identify rate limit window'
                ],
                'recovery_steps': [
                    'Implement exponential backoff',
                    'Queue requests for later processing',
                    'Distribute load across time windows',
                    'Switch to different API key if available'
                ],
                'preventive_measures': [
                    'Implement request throttling',
                    'Add rate limit monitoring',
                    'Optimize API call patterns'
                ]
            },
            'resource': {
                'immediate_actions': [
                    'Check system resource usage',
                    'Identify resource bottleneck'
                ],
                'recovery_steps': [
                    'Free up memory/disk space',
                    'Restart agent with increased limits',
                    'Clear temporary files and caches',
                    'Scale down concurrent operations'
                ],
                'preventive_measures': [
                    'Implement resource monitoring',
                    'Add automatic cleanup routines',
                    'Configure appropriate resource limits'
                ]
            },
            'crash': {
                'immediate_actions': [
                    'Collect crash dump/stack trace',
                    'Check exit code and signals'
                ],
                'recovery_steps': [
                    'Restart agent with recovery mode',
                    'Clear corrupted state files',
                    'Restore from last known good state',
                    'Run with debug logging enabled'
                ],
                'preventive_measures': [
                    'Add exception handling',
                    'Implement graceful shutdown',
                    'Add health check endpoints'
                ]
            },
            'copilot': {
                'immediate_actions': [
                    'Verify Copilot subscription status',
                    'Check GitHub authentication'
                ],
                'recovery_steps': [
                    'Re-authenticate with GitHub',
                    'Clear Copilot cache',
                    'Switch to alternative AI service',
                    'Restart VS Code/IDE'
                ],
                'preventive_measures': [
                    'Monitor subscription expiry',
                    'Implement fallback AI providers',
                    'Cache Copilot responses'
                ]
            },
            'performance': {
                'immediate_actions': [
                    'Measure current performance metrics',
                    'Identify performance bottlenecks'
                ],
                'recovery_steps': [
                    'Optimize resource allocation',
                    'Reduce concurrent operations',
                    'Clear performance-impacting caches',
                    'Adjust timeout values'
                ],
                'preventive_measures': [
                    'Implement performance monitoring',
                    'Add caching layers',
                    'Optimize algorithms and queries'
                ]
            }
        }
        
        plan = resolution_plans.get(issue_type, {
            'immediate_actions': ['Investigate issue manually'],
            'recovery_steps': ['Restart agent', 'Check logs'],
            'preventive_measures': ['Add monitoring for this issue type']
        })
        
        # Add context-specific recommendations
        if context:
            plan['context'] = context
            plan['priority'] = self._calculate_priority(issue_type, agent_name)
            plan['estimated_recovery_time'] = self._estimate_recovery_time(issue_type)
        
        plan['agent_name'] = agent_name
        plan['issue_type'] = issue_type
        plan['generated_at'] = datetime.now().isoformat()
        
        return plan
    
    def _calculate_priority(self, issue_type: str, agent_name: str) -> str:
        """Calculate resolution priority based on severity and frequency"""
        severity = self.failure_patterns[issue_type]['severity']
        recent_issues = len([i for i in self.issue_history[agent_name] 
                           if i['issue_type'] == issue_type])
        
        if severity == 'CRITICAL' or recent_issues > 5:
            return 'P1-URGENT'
        elif severity == 'HIGH' or recent_issues > 3:
            return 'P2-HIGH'
        elif severity == 'MEDIUM':
            return 'P3-MEDIUM'
        else:
            return 'P4-LOW'
    
    def _estimate_recovery_time(self, issue_type: str) -> str:
        """Estimate time to recover from issue"""
        recovery_times = {
            'network': '30-60 seconds',
            'auth': '1-2 minutes',
            'rate_limit': '5-15 minutes',
            'resource': '2-5 minutes',
            'crash': '1-3 minutes',
            'copilot': '2-5 minutes',
            'performance': '3-10 minutes'
        }
        return recovery_times.get(issue_type, '5-10 minutes')
    
    def monitor_agents(self):
        """Continuously monitor agents from dashboard API"""
        logger.info("Starting agent monitoring...")
        
        while self.monitoring:
            try:
                # Fetch agent data from dashboard
                response = requests.get(self.api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Process agent outputs
                    if 'agent_outputs' in data:
                        for agent_name, output_data in data['agent_outputs'].items():
                            if isinstance(output_data, dict) and 'output' in output_data:
                                output = output_data['output']
                                if output and output.strip():
                                    issues = self.analyze_agent_output(agent_name, output)
                                    
                                    # Generate resolution plans for detected issues
                                    for issue in issues:
                                        plan = self.generate_resolution_plan(
                                            issue['issue_type'],
                                            agent_name,
                                            {'detected_issue': issue}
                                        )
                                        self.resolution_plans[f"{agent_name}_{issue['issue_type']}"] = plan
                                        self._save_resolution_plan(plan)
                    
                    # Update agent states
                    if 'agent_data' in data:
                        self.agent_states = data['agent_data']
                
            except requests.RequestException as e:
                logger.error(f"Failed to fetch dashboard data: {e}")
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(3)  # Check every 3 seconds
    
    def _save_resolution_plan(self, plan: Dict[str, Any]):
        """Save resolution plan to file for self-healing system"""
        filename = f"resolution_plans/{plan['agent_name']}_{plan['issue_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path("resolution_plans").mkdir(exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_agents, daemon=True)
            self.monitor_thread.start()
            logger.info("Monitoring thread started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Monitoring thread stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current detection metrics"""
        return {
            'total_issues': self.metrics['total_issues_detected'],
            'issues_by_type': dict(self.metrics['issues_by_type']),
            'issues_by_agent': dict(self.metrics['issues_by_agent']),
            'detection_rate': self._calculate_detection_rate(),
            'top_issues': self._get_top_issues(),
            'agent_health_scores': self._calculate_health_scores()
        }
    
    def _calculate_detection_rate(self) -> float:
        """Calculate issue detection rate per minute"""
        if not self.metrics['detection_times']:
            return 0.0
        
        recent_times = [t for t in self.metrics['detection_times'] 
                       if t > datetime.now() - timedelta(minutes=5)]
        return len(recent_times) / 5.0  # Issues per minute
    
    def _get_top_issues(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most common issue types"""
        sorted_issues = sorted(self.metrics['issues_by_type'].items(), 
                             key=lambda x: x[1], reverse=True)
        return sorted_issues[:limit]
    
    def _calculate_health_scores(self) -> Dict[str, float]:
        """Calculate health score for each agent (0-100)"""
        health_scores = {}
        
        for agent_name in self.agent_states.keys():
            issues = self.issue_history[agent_name]
            recent_issues = [i for i in issues 
                           if datetime.fromisoformat(i['timestamp']) > 
                           datetime.now() - timedelta(minutes=30)]
            
            # Base score
            score = 100.0
            
            # Deduct for recent issues
            for issue in recent_issues:
                if issue['severity'] == 'CRITICAL':
                    score -= 20
                elif issue['severity'] == 'HIGH':
                    score -= 10
                elif issue['severity'] == 'MEDIUM':
                    score -= 5
            
            health_scores[agent_name] = max(0, score)
        
        return health_scores
    
    def save_progress(self):
        """Save progress to JSON file for coordination"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'component': 'intelligent-issue-detector',
            'status': 'operational',
            'metrics': self.get_metrics(),
            'active_resolution_plans': len(self.resolution_plans),
            'monitoring_active': self.monitoring
        }
        
        with open('claude_opus_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
        
        logger.info("Progress saved to claude_opus_progress.json")


def main():
    """Main execution function"""
    logger.info("Starting Intelligent Issue Detector...")
    
    # Initialize detector
    detector = IssueDetector()
    
    # Start monitoring
    detector.start_monitoring()
    
    try:
        # Keep running and periodically save progress
        while True:
            time.sleep(30)  # Save progress every 30 seconds
            detector.save_progress()
            
            # Log current metrics
            metrics = detector.get_metrics()
            logger.info(f"Detection metrics: {metrics['total_issues']} total issues, "
                       f"Detection rate: {metrics['detection_rate']:.2f}/min")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        detector.stop_monitoring()
        detector.save_progress()
        sys.exit(0)


if __name__ == "__main__":
    main()
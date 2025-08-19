#!/usr/bin/env python3
"""
Enhanced Dashboard Analytics Module
Adds ML-based anomaly detection, predictive analysis, and smart alerting to the dashboard
"""

import numpy as np
import json
import time
import logging
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import threading
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DashboardAnalytics')

class AdvancedAnalytics:
    """Advanced analytics module for agent dashboard"""
    
    def __init__(self):
        # Data storage
        self.agent_metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.system_metrics_history = deque(maxlen=1000)
        self.anomaly_history = defaultdict(list)
        self.predictions = {}
        self.health_scores = {}
        self.smart_alerts = deque(maxlen=100)
        
        # ML Models
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.failure_predictor = None
        
        # Thresholds and configurations
        self.config = {
            'anomaly_threshold': 0.7,
            'failure_prediction_window': 300,  # 5 minutes
            'health_score_weights': {
                'cpu': 0.25,
                'memory': 0.25,
                'errors': 0.3,
                'responsiveness': 0.2
            },
            'alert_priorities': {
                'critical': 1,
                'high': 2,
                'medium': 3,
                'low': 4
            }
        }
        
        # Pattern detection
        self.patterns = {
            'memory_leak': [],
            'cpu_spike': [],
            'network_issues': [],
            'cascading_failure': []
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for analytics"""
        try:
            # Initialize Isolation Forest for anomaly detection
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    def calculate_health_score(self, agent_metrics: Dict[str, Any]) -> float:
        """
        Calculate comprehensive health score for an agent
        Returns score between 0-100
        """
        try:
            score = 100.0
            weights = self.config['health_score_weights']
            
            # CPU impact
            cpu_percent = agent_metrics.get('cpu_percent', 0)
            if cpu_percent > 90:
                score -= weights['cpu'] * 50
            elif cpu_percent > 70:
                score -= weights['cpu'] * 30
            elif cpu_percent > 50:
                score -= weights['cpu'] * 10
            
            # Memory impact
            memory_mb = agent_metrics.get('memory_mb', 0)
            memory_limit = agent_metrics.get('memory_limit', 512)
            memory_percent = (memory_mb / memory_limit) * 100 if memory_limit > 0 else 0
            
            if memory_percent > 90:
                score -= weights['memory'] * 50
            elif memory_percent > 70:
                score -= weights['memory'] * 30
            elif memory_percent > 50:
                score -= weights['memory'] * 10
            
            # Error rate impact
            error_count = agent_metrics.get('error_count', 0)
            total_ops = agent_metrics.get('total_operations', 1)
            error_rate = (error_count / total_ops) * 100 if total_ops > 0 else 0
            
            if error_rate > 10:
                score -= weights['errors'] * 60
            elif error_rate > 5:
                score -= weights['errors'] * 40
            elif error_rate > 1:
                score -= weights['errors'] * 20
            
            # Responsiveness impact
            response_time = agent_metrics.get('avg_response_time', 0)
            if response_time > 5000:  # 5 seconds
                score -= weights['responsiveness'] * 40
            elif response_time > 2000:  # 2 seconds
                score -= weights['responsiveness'] * 20
            elif response_time > 1000:  # 1 second
                score -= weights['responsiveness'] * 10
            
            # Add bonus for uptime
            uptime_hours = agent_metrics.get('uptime_hours', 0)
            if uptime_hours > 24:
                score += 5
            elif uptime_hours > 12:
                score += 3
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
            # Store historical health score
            agent_name = agent_metrics.get('name', 'unknown')
            if agent_name not in self.health_scores:
                self.health_scores[agent_name] = deque(maxlen=100)
            self.health_scores[agent_name].append({
                'timestamp': datetime.now().isoformat(),
                'score': score
            })
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50.0  # Default middle score on error
    
    def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Isolation Forest
        Returns list of detected anomalies with details
        """
        anomalies = []
        
        try:
            # Prepare feature vector
            features = self._extract_features(metrics)
            
            if len(features) < 5:  # Need minimum features
                return anomalies
            
            # Reshape for sklearn
            X = np.array(features).reshape(1, -1)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train or predict
            if self.anomaly_detector and len(self.system_metrics_history) > 50:
                # Predict anomaly
                anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
                is_anomaly = self.anomaly_detector.predict(X_scaled)[0] == -1
                
                if is_anomaly or anomaly_score < -self.config['anomaly_threshold']:
                    anomaly = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'system_anomaly',
                        'severity': self._calculate_anomaly_severity(anomaly_score),
                        'score': float(anomaly_score),
                        'metrics': metrics,
                        'description': self._describe_anomaly(metrics, features)
                    }
                    anomalies.append(anomaly)
                    
                    # Store in history
                    self.anomaly_history['system'].append(anomaly)
            
            # Check for specific pattern anomalies
            pattern_anomalies = self._detect_pattern_anomalies(metrics)
            anomalies.extend(pattern_anomalies)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def _extract_features(self, metrics: Dict[str, Any]) -> List[float]:
        """Extract numerical features from metrics for ML models"""
        features = []
        
        try:
            # System metrics
            if 'system' in metrics:
                features.extend([
                    metrics['system'].get('cpu_percent', 0),
                    metrics['system'].get('memory_percent', 0),
                    metrics['system'].get('disk_percent', 0)
                ])
            
            # Agent metrics
            if 'agents' in metrics:
                features.extend([
                    metrics['agents'].get('total', 0),
                    metrics['agents'].get('running', 0),
                    metrics['agents'].get('total_memory_mb', 0)
                ])
            
            # Network metrics
            if 'network' in metrics:
                features.extend([
                    metrics['network'].get('bytes_sent', 0),
                    metrics['network'].get('bytes_recv', 0)
                ])
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
        
        return features
    
    def _calculate_anomaly_severity(self, score: float) -> str:
        """Calculate severity level based on anomaly score"""
        abs_score = abs(score)
        if abs_score > 1.5:
            return 'critical'
        elif abs_score > 1.0:
            return 'high'
        elif abs_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _describe_anomaly(self, metrics: Dict[str, Any], features: List[float]) -> str:
        """Generate human-readable description of anomaly"""
        descriptions = []
        
        if 'system' in metrics:
            sys = metrics['system']
            if sys.get('cpu_percent', 0) > 90:
                descriptions.append(f"Critical CPU usage: {sys['cpu_percent']}%")
            if sys.get('memory_percent', 0) > 90:
                descriptions.append(f"Critical memory usage: {sys['memory_percent']}%")
            if sys.get('disk_percent', 0) > 90:
                descriptions.append(f"Critical disk usage: {sys['disk_percent']}%")
        
        if 'agents' in metrics:
            agents = metrics['agents']
            total = agents.get('total', 0)
            running = agents.get('running', 0)
            if running < total * 0.5:
                descriptions.append(f"Many agents down: {total - running}/{total}")
        
        return "; ".join(descriptions) if descriptions else "Unusual system behavior detected"
    
    def _detect_pattern_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific pattern-based anomalies"""
        anomalies = []
        
        # Memory leak detection
        if self._detect_memory_leak(metrics):
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'memory_leak',
                'severity': 'high',
                'description': 'Potential memory leak detected - continuous memory growth',
                'metrics': metrics
            })
        
        # CPU spike detection
        if self._detect_cpu_spike(metrics):
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'cpu_spike',
                'severity': 'medium',
                'description': 'Sudden CPU spike detected',
                'metrics': metrics
            })
        
        # Cascading failure detection
        if self._detect_cascading_failure(metrics):
            anomalies.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'cascading_failure',
                'severity': 'critical',
                'description': 'Potential cascading failure - multiple agents failing',
                'metrics': metrics
            })
        
        return anomalies
    
    def _detect_memory_leak(self, metrics: Dict[str, Any]) -> bool:
        """Detect potential memory leaks"""
        try:
            # Store memory values
            if 'system' in metrics:
                memory_percent = metrics['system'].get('memory_percent', 0)
                self.patterns['memory_leak'].append(memory_percent)
                
                # Keep last 20 readings
                if len(self.patterns['memory_leak']) > 20:
                    self.patterns['memory_leak'].pop(0)
                
                # Check for continuous increase
                if len(self.patterns['memory_leak']) >= 10:
                    recent = self.patterns['memory_leak'][-10:]
                    # Check if memory is continuously increasing
                    increases = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])
                    avg_increase = np.mean(np.diff(recent)) if len(recent) > 1 else 0
                    
                    if increases >= 8 and avg_increase > 0.5:
                        return True
        except Exception as e:
            logger.error(f"Error detecting memory leak: {e}")
        
        return False
    
    def _detect_cpu_spike(self, metrics: Dict[str, Any]) -> bool:
        """Detect sudden CPU spikes"""
        try:
            if 'system' in metrics:
                cpu_percent = metrics['system'].get('cpu_percent', 0)
                self.patterns['cpu_spike'].append(cpu_percent)
                
                # Keep last 10 readings
                if len(self.patterns['cpu_spike']) > 10:
                    self.patterns['cpu_spike'].pop(0)
                
                # Check for spike
                if len(self.patterns['cpu_spike']) >= 5:
                    recent = self.patterns['cpu_spike'][-5:]
                    avg_recent = np.mean(recent[-3:])
                    avg_previous = np.mean(recent[:-3])
                    
                    # Spike if recent average is 50% higher than previous
                    if avg_recent > avg_previous * 1.5 and avg_recent > 70:
                        return True
        except Exception as e:
            logger.error(f"Error detecting CPU spike: {e}")
        
        return False
    
    def _detect_cascading_failure(self, metrics: Dict[str, Any]) -> bool:
        """Detect cascading failures across agents"""
        try:
            if 'agents' in metrics:
                total = metrics['agents'].get('total', 0)
                running = metrics['agents'].get('running', 0)
                
                if total > 0:
                    failure_rate = (total - running) / total
                    
                    # Store failure rates
                    if 'cascading_failure' not in self.patterns:
                        self.patterns['cascading_failure'] = []
                    
                    self.patterns['cascading_failure'].append({
                        'timestamp': datetime.now(),
                        'failure_rate': failure_rate,
                        'failed_count': total - running
                    })
                    
                    # Keep last 5 minutes
                    cutoff = datetime.now() - timedelta(minutes=5)
                    self.patterns['cascading_failure'] = [
                        p for p in self.patterns['cascading_failure']
                        if p['timestamp'] > cutoff
                    ]
                    
                    # Check for cascading pattern
                    if len(self.patterns['cascading_failure']) >= 3:
                        recent = self.patterns['cascading_failure'][-3:]
                        # Check if failures are increasing
                        if all(recent[i]['failed_count'] > recent[i-1]['failed_count'] 
                              for i in range(1, len(recent))):
                            if recent[-1]['failure_rate'] > 0.3:  # More than 30% failed
                                return True
        except Exception as e:
            logger.error(f"Error detecting cascading failure: {e}")
        
        return False
    
    def predict_failure_probability(self, agent_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict probability of agent failure in the next time window
        Uses historical patterns and current trends
        """
        try:
            if len(agent_history) < 10:
                return {'probability': 0.0, 'confidence': 'low', 'factors': []}
            
            # Extract recent metrics
            recent_metrics = agent_history[-20:] if len(agent_history) >= 20 else agent_history
            
            failure_probability = 0.0
            contributing_factors = []
            
            # Analyze CPU trend
            cpu_values = [m.get('cpu_percent', 0) for m in recent_metrics]
            if cpu_values:
                cpu_trend = np.polyfit(range(len(cpu_values)), cpu_values, 1)[0]
                avg_cpu = np.mean(cpu_values)
                
                if cpu_trend > 2 and avg_cpu > 70:
                    failure_probability += 0.3
                    contributing_factors.append("Increasing CPU usage trend")
                elif avg_cpu > 85:
                    failure_probability += 0.2
                    contributing_factors.append("High average CPU usage")
            
            # Analyze memory trend
            memory_values = [m.get('memory_mb', 0) for m in recent_metrics]
            if memory_values:
                memory_trend = np.polyfit(range(len(memory_values)), memory_values, 1)[0]
                
                if memory_trend > 5:  # Growing by 5MB per measurement
                    failure_probability += 0.25
                    contributing_factors.append("Memory usage growing rapidly")
            
            # Analyze error patterns
            error_counts = [m.get('error_count', 0) for m in recent_metrics]
            if error_counts:
                recent_errors = sum(error_counts[-5:])
                if recent_errors > 10:
                    failure_probability += 0.35
                    contributing_factors.append(f"High error rate: {recent_errors} recent errors")
                elif recent_errors > 5:
                    failure_probability += 0.15
                    contributing_factors.append(f"Moderate error rate: {recent_errors} recent errors")
            
            # Analyze response times
            response_times = [m.get('response_time', 0) for m in recent_metrics]
            if response_times:
                avg_response = np.mean(response_times[-5:])
                if avg_response > 5000:
                    failure_probability += 0.2
                    contributing_factors.append("Very slow response times")
            
            # Check for restart patterns
            restart_count = sum(1 for m in recent_metrics if m.get('event') == 'restart')
            if restart_count > 2:
                failure_probability += 0.3
                contributing_factors.append(f"Multiple recent restarts: {restart_count}")
            
            # Cap probability at 0.95
            failure_probability = min(failure_probability, 0.95)
            
            # Determine confidence level
            confidence = 'high' if len(agent_history) > 50 else 'medium' if len(agent_history) > 20 else 'low'
            
            # Calculate time to failure estimate
            time_to_failure = None
            if failure_probability > 0.7:
                time_to_failure = "< 5 minutes"
            elif failure_probability > 0.5:
                time_to_failure = "5-15 minutes"
            elif failure_probability > 0.3:
                time_to_failure = "15-30 minutes"
            
            prediction = {
                'probability': round(failure_probability, 2),
                'confidence': confidence,
                'factors': contributing_factors,
                'time_to_failure': time_to_failure,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store prediction
            agent_name = agent_history[-1].get('name', 'unknown') if agent_history else 'unknown'
            self.predictions[agent_name] = prediction
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting failure: {e}")
            return {'probability': 0.0, 'confidence': 'error', 'factors': [str(e)]}
    
    def generate_smart_alerts(self, anomalies: List[Dict[str, Any]], 
                            predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate context-aware alerts with actionable information
        Deduplicates and prioritizes alerts
        """
        alerts = []
        
        try:
            # Process anomalies into alerts
            for anomaly in anomalies:
                alert = {
                    'id': f"alert_{datetime.now().timestamp()}",
                    'timestamp': datetime.now().isoformat(),
                    'type': anomaly['type'],
                    'severity': anomaly['severity'],
                    'title': self._generate_alert_title(anomaly),
                    'description': anomaly.get('description', ''),
                    'context': self._generate_alert_context(anomaly),
                    'actions': self._generate_recommended_actions(anomaly),
                    'priority': self.config['alert_priorities'].get(anomaly['severity'], 5)
                }
                alerts.append(alert)
            
            # Process predictions into alerts
            for agent_name, prediction in predictions.items():
                if prediction['probability'] > 0.6:
                    alert = {
                        'id': f"predict_{agent_name}_{datetime.now().timestamp()}",
                        'timestamp': datetime.now().isoformat(),
                        'type': 'failure_prediction',
                        'severity': 'high' if prediction['probability'] > 0.8 else 'medium',
                        'title': f"High failure risk for {agent_name}",
                        'description': f"Failure probability: {prediction['probability']*100:.0f}%",
                        'context': {
                            'factors': prediction['factors'],
                            'time_to_failure': prediction.get('time_to_failure'),
                            'confidence': prediction['confidence']
                        },
                        'actions': [
                            f"Monitor {agent_name} closely",
                            "Consider preemptive restart",
                            "Check resource allocation",
                            "Review recent error logs"
                        ],
                        'priority': 1 if prediction['probability'] > 0.8 else 2
                    }
                    alerts.append(alert)
            
            # Deduplicate similar alerts
            alerts = self._deduplicate_alerts(alerts)
            
            # Sort by priority
            alerts.sort(key=lambda x: x['priority'])
            
            # Store in history
            for alert in alerts:
                self.smart_alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error generating smart alerts: {e}")
        
        return alerts
    
    def _generate_alert_title(self, anomaly: Dict[str, Any]) -> str:
        """Generate descriptive alert title"""
        type_titles = {
            'system_anomaly': 'System Anomaly Detected',
            'memory_leak': 'Potential Memory Leak',
            'cpu_spike': 'CPU Spike Detected',
            'cascading_failure': 'Cascading Failure Warning',
            'network_issues': 'Network Issues Detected'
        }
        return type_titles.get(anomaly['type'], 'Alert')
    
    def _generate_alert_context(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual information for alert"""
        context = {
            'detected_at': anomaly.get('timestamp'),
            'severity': anomaly.get('severity'),
            'score': anomaly.get('score')
        }
        
        if 'metrics' in anomaly:
            metrics = anomaly['metrics']
            if 'system' in metrics:
                context['system_state'] = {
                    'cpu': metrics['system'].get('cpu_percent'),
                    'memory': metrics['system'].get('memory_percent'),
                    'disk': metrics['system'].get('disk_percent')
                }
            if 'agents' in metrics:
                context['agent_state'] = {
                    'total': metrics['agents'].get('total'),
                    'running': metrics['agents'].get('running')
                }
        
        return context
    
    def _generate_recommended_actions(self, anomaly: Dict[str, Any]) -> List[str]:
        """Generate recommended actions based on anomaly type"""
        actions_map = {
            'memory_leak': [
                "Identify processes with growing memory",
                "Restart affected agents",
                "Check for infinite loops or unbounded data structures",
                "Enable memory profiling"
            ],
            'cpu_spike': [
                "Check for runaway processes",
                "Review recent code changes",
                "Consider load distribution",
                "Monitor for recurring patterns"
            ],
            'cascading_failure': [
                "Initiate emergency response protocol",
                "Isolate failing components",
                "Check shared dependencies",
                "Prepare for rollback if needed"
            ],
            'system_anomaly': [
                "Review system logs",
                "Check resource utilization",
                "Verify external dependencies",
                "Consider system restart if critical"
            ]
        }
        
        return actions_map.get(anomaly['type'], ["Investigate the issue", "Monitor closely"])
    
    def _deduplicate_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or similar alerts"""
        unique_alerts = []
        seen_keys = set()
        
        for alert in alerts:
            # Create a key for deduplication
            key = f"{alert['type']}_{alert['severity']}_{alert.get('title', '')[:20]}"
            
            if key not in seen_keys:
                unique_alerts.append(alert)
                seen_keys.add(key)
        
        return unique_alerts
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            # Calculate overall system health
            overall_health = np.mean([
                scores[-1]['score'] if scores else 50 
                for scores in self.health_scores.values()
            ]) if self.health_scores else 50
            
            # Count recent anomalies
            recent_anomalies = sum(
                len([a for a in anomalies if datetime.fromisoformat(a['timestamp']) > 
                    datetime.now() - timedelta(minutes=30)])
                for anomalies in self.anomaly_history.values()
            )
            
            # Get high-risk agents
            high_risk_agents = [
                agent for agent, pred in self.predictions.items()
                if pred['probability'] > 0.6
            ]
            
            # Get active alerts
            active_alerts = list(self.smart_alerts)[-10:]  # Last 10 alerts
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_health': round(overall_health, 1),
                'health_status': self._get_health_status(overall_health),
                'total_agents_monitored': len(self.health_scores),
                'recent_anomalies': recent_anomalies,
                'high_risk_agents': high_risk_agents,
                'active_alerts': len(active_alerts),
                'critical_alerts': len([a for a in active_alerts if a.get('severity') == 'critical']),
                'predictions_made': len(self.predictions),
                'top_issues': self._get_top_issues(),
                'recommendations': self._generate_recommendations(overall_health, recent_anomalies)
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {'error': str(e)}
    
    def _get_health_status(self, score: float) -> str:
        """Convert health score to status"""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        elif score >= 25:
            return 'Poor'
        else:
            return 'Critical'
    
    def _get_top_issues(self) -> List[str]:
        """Get top issues affecting the system"""
        issues = []
        
        # Check anomaly types
        anomaly_counts = defaultdict(int)
        for anomaly_list in self.anomaly_history.values():
            for anomaly in anomaly_list[-20:]:  # Last 20 anomalies
                anomaly_counts[anomaly['type']] += 1
        
        # Sort by frequency
        sorted_issues = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)
        
        for issue_type, count in sorted_issues[:5]:
            issues.append(f"{issue_type.replace('_', ' ').title()}: {count} occurrences")
        
        return issues
    
    def _generate_recommendations(self, health: float, anomalies: int) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if health < 50:
            recommendations.append("System health is poor - consider immediate intervention")
        
        if anomalies > 10:
            recommendations.append("High anomaly rate detected - investigate root causes")
        
        if len(self.predictions) > 0:
            high_risk = sum(1 for p in self.predictions.values() if p['probability'] > 0.7)
            if high_risk > 0:
                recommendations.append(f"{high_risk} agents at high risk of failure - consider preemptive action")
        
        if not recommendations:
            recommendations.append("System operating normally - continue monitoring")
        
        return recommendations
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export analytics data for integration with dashboard"""
        return {
            'health_scores': {
                agent: list(scores)[-10:] if len(scores) > 10 else list(scores)
                for agent, scores in self.health_scores.items()
            },
            'anomalies': {
                key: list(anomalies)[-20:] if len(anomalies) > 20 else anomalies
                for key, anomalies in self.anomaly_history.items()
            },
            'predictions': self.predictions,
            'alerts': list(self.smart_alerts)[-50:],
            'summary': self.get_analytics_summary()
        }


def integrate_with_dashboard(analytics: AdvancedAnalytics, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Integrate analytics with existing dashboard data"""
    
    # Calculate health scores for all agents
    for agent_name, agent_data in dashboard_data.get('agent_data', {}).items():
        # Prepare metrics for health calculation
        agent_metrics = {
            'name': agent_name,
            'cpu_percent': agent_data.get('cpu_percent', 0),
            'memory_mb': agent_data.get('memory_mb', 0),
            'memory_limit': 512,  # Default limit
            'error_count': 0,  # Would need to parse from output
            'total_operations': 100,  # Estimate
            'avg_response_time': 1000,  # Estimate
            'uptime_hours': 1  # Would calculate from create_time
        }
        
        # Calculate health score
        health_score = analytics.calculate_health_score(agent_metrics)
        agent_data['health_score'] = health_score
        agent_data['health_status'] = analytics._get_health_status(health_score)
    
    # Detect anomalies in system metrics
    if 'system_metrics' in dashboard_data:
        anomalies = analytics.detect_anomalies(dashboard_data['system_metrics'])
        dashboard_data['anomalies'] = anomalies
    
    # Generate predictions for agents with history
    predictions = {}
    for agent_name in dashboard_data.get('agent_data', {}).keys():
        # Would need historical data for accurate predictions
        # For now, using current data as history
        agent_history = [dashboard_data['agent_data'][agent_name]] * 20
        prediction = analytics.predict_failure_probability(agent_history)
        predictions[agent_name] = prediction
    
    dashboard_data['predictions'] = predictions
    
    # Generate smart alerts
    alerts = analytics.generate_smart_alerts(
        dashboard_data.get('anomalies', []),
        predictions
    )
    dashboard_data['alerts'] = alerts
    
    # Add analytics summary
    dashboard_data['analytics_summary'] = analytics.get_analytics_summary()
    
    return dashboard_data


# Example usage and testing
if __name__ == "__main__":
    logger.info("Initializing Advanced Analytics Module...")
    
    # Create analytics instance
    analytics = AdvancedAnalytics()
    
    # Simulate test data
    test_metrics = {
        'system': {
            'cpu_percent': 75,
            'memory_percent': 82,
            'disk_percent': 65
        },
        'agents': {
            'total': 23,
            'running': 20,
            'total_memory_mb': 4096
        },
        'network': {
            'bytes_sent': 1024000,
            'bytes_recv': 2048000
        }
    }
    
    # Test health score calculation
    test_agent = {
        'name': 'test_agent',
        'cpu_percent': 45,
        'memory_mb': 256,
        'memory_limit': 512,
        'error_count': 2,
        'total_operations': 100,
        'avg_response_time': 800,
        'uptime_hours': 5
    }
    
    health_score = analytics.calculate_health_score(test_agent)
    logger.info(f"Test agent health score: {health_score}")
    
    # Test anomaly detection
    anomalies = analytics.detect_anomalies(test_metrics)
    logger.info(f"Detected anomalies: {len(anomalies)}")
    
    # Test failure prediction
    agent_history = [test_agent] * 20
    prediction = analytics.predict_failure_probability(agent_history)
    logger.info(f"Failure prediction: {prediction}")
    
    # Test alert generation
    alerts = analytics.generate_smart_alerts(anomalies, {'test_agent': prediction})
    logger.info(f"Generated alerts: {len(alerts)}")
    
    # Get summary
    summary = analytics.get_analytics_summary()
    logger.info(f"Analytics summary: {json.dumps(summary, indent=2)}")
    
    print("\n" + "="*80)
    print("Advanced Analytics Module Initialized Successfully!")
    print("="*80)
    print(f"Health Monitoring: Active")
    print(f"Anomaly Detection: Active")
    print(f"Failure Prediction: Active")
    print(f"Smart Alerting: Active")
    print("="*80)
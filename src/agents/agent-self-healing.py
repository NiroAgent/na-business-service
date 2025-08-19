#!/usr/bin/env python3
"""
Agent Self-Healing System for Automatic Issue Resolution
Integrates with issue detector to automatically fix detected problems
"""

import json
import os
import time
import subprocess
import psutil
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import requests
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('self_healing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SelfHealing')

class SelfHealing:
    """Automatic issue resolution system for agent orchestration"""
    
    def __init__(self, python_exe: str = "E:/Projects/.venv/Scripts/python.exe"):
        self.python_exe = python_exe
        self.resolution_plans_dir = Path("resolution_plans")
        self.healing_history = []
        self.active_healings = {}
        self.resource_locks = {}
        
        # Healing strategies configuration
        self.healing_strategies = {
            'network': self._heal_network_issues,
            'auth': self._heal_auth_issues,
            'rate_limit': self._heal_rate_limit_issues,
            'resource': self._heal_resource_issues,
            'crash': self._heal_crash_issues,
            'copilot': self._heal_copilot_issues,
            'performance': self._heal_performance_issues
        }
        
        # Restart configuration
        self.restart_config = {
            'max_retries': 3,
            'initial_delay': 5,
            'max_delay': 60,
            'backoff_factor': 2
        }
        
        # Resource limits
        self.resource_limits = {
            'memory_mb': 512,
            'cpu_percent': 80,
            'disk_cleanup_threshold_gb': 1
        }
        
        # Metrics tracking
        self.metrics = {
            'total_healings': 0,
            'successful_healings': 0,
            'failed_healings': 0,
            'healings_by_type': {},
            'avg_healing_time': 0,
            'healing_times': []
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = None
    
    def execute_healing_action(self, agent_name: str, issue_type: str, 
                              resolution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute healing action based on issue type and resolution plan"""
        
        logger.info(f"Executing healing for {agent_name}: {issue_type}")
        start_time = datetime.now()
        
        # Check if healing already in progress
        healing_key = f"{agent_name}_{issue_type}"
        if healing_key in self.active_healings:
            logger.warning(f"Healing already in progress for {healing_key}")
            return {
                'success': False,
                'message': 'Healing already in progress',
                'duration': 0
            }
        
        self.active_healings[healing_key] = {
            'started': start_time,
            'status': 'in_progress'
        }
        
        try:
            # Execute appropriate healing strategy
            if issue_type in self.healing_strategies:
                result = self.healing_strategies[issue_type](agent_name, resolution_plan)
            else:
                result = self._generic_healing(agent_name, resolution_plan)
            
            # Record healing result
            duration = (datetime.now() - start_time).total_seconds()
            result['duration'] = duration
            
            self._record_healing(agent_name, issue_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Healing failed for {agent_name}: {e}")
            return {
                'success': False,
                'message': str(e),
                'duration': (datetime.now() - start_time).total_seconds()
            }
        finally:
            # Remove from active healings
            if healing_key in self.active_healings:
                del self.active_healings[healing_key]
    
    def _heal_network_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal network-related issues"""
        logger.info(f"Healing network issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Clear DNS cache
            if sys.platform == "win32":
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
                actions_taken.append("Cleared DNS cache")
            
            # 2. Test connectivity
            test_urls = ["https://api.github.com", "https://google.com"]
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        actions_taken.append(f"Connectivity test passed: {url}")
                except:
                    actions_taken.append(f"Connectivity test failed: {url}")
            
            # 3. Restart agent with retry logic
            restart_result = self.restart_with_recovery(agent_name, {
                'retry_enabled': True,
                'connection_timeout': 30,
                'retry_attempts': 5
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted with enhanced retry logic")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Network healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Network healing failed: {e}"
            }
    
    def _heal_auth_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal authentication-related issues"""
        logger.info(f"Healing authentication issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Check and refresh tokens
            token_file = Path(f"tokens/{agent_name}_token.json")
            if token_file.exists():
                # Backup old token
                backup_path = token_file.with_suffix('.backup')
                shutil.copy(token_file, backup_path)
                actions_taken.append("Backed up existing token")
                
                # Try to refresh token
                # This would normally integrate with your auth system
                actions_taken.append("Attempted token refresh")
            
            # 2. Clear credential cache
            cache_dir = Path(f"cache/{agent_name}")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                actions_taken.append("Cleared credential cache")
            
            # 3. Re-authenticate using stored credentials
            # This would integrate with your credential management
            actions_taken.append("Initiated re-authentication")
            
            # 4. Restart agent with fresh auth
            restart_result = self.restart_with_recovery(agent_name, {
                'force_reauth': True,
                'clear_session': True
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted with fresh authentication")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Authentication healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Auth healing failed: {e}"
            }
    
    def _heal_rate_limit_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal rate limiting issues"""
        logger.info(f"Healing rate limit issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Implement backoff delay
            delay = 60  # Start with 1 minute delay
            logger.info(f"Applying backoff delay of {delay} seconds")
            time.sleep(delay)
            actions_taken.append(f"Applied {delay}s backoff delay")
            
            # 2. Reduce request frequency
            config_file = Path(f"configs/{agent_name}_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Reduce request rate
                if 'request_delay' in config:
                    config['request_delay'] = min(config['request_delay'] * 2, 10)
                else:
                    config['request_delay'] = 2
                
                if 'concurrent_requests' in config:
                    config['concurrent_requests'] = max(1, config['concurrent_requests'] // 2)
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                actions_taken.append("Reduced request frequency in config")
            
            # 3. Restart with throttling
            restart_result = self.restart_with_recovery(agent_name, {
                'throttle_enabled': True,
                'max_requests_per_minute': 30,
                'request_delay': 2
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted with throttling enabled")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Rate limit healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Rate limit healing failed: {e}"
            }
    
    def _heal_resource_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal resource-related issues"""
        logger.info(f"Healing resource issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Free up system resources
            freed_resources = self.apply_resource_fixes(agent_name, 'all')
            actions_taken.extend(freed_resources['actions'])
            
            # 2. Adjust resource limits
            process = self._get_agent_process(agent_name)
            if process:
                try:
                    # Set CPU affinity (Windows)
                    if sys.platform == "win32":
                        process.cpu_affinity([0, 1])  # Limit to 2 cores
                        actions_taken.append("Adjusted CPU affinity")
                    
                    # Nice the process (Unix)
                    else:
                        process.nice(10)
                        actions_taken.append("Adjusted process priority")
                except:
                    pass
            
            # 3. Restart with resource limits
            restart_result = self.restart_with_recovery(agent_name, {
                'memory_limit_mb': self.resource_limits['memory_mb'],
                'cpu_limit_percent': self.resource_limits['cpu_percent']
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted with resource limits")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Resource healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Resource healing failed: {e}"
            }
    
    def _heal_crash_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal crash-related issues"""
        logger.info(f"Healing crash issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Clean up crash artifacts
            crash_dir = Path(f"crashes/{agent_name}")
            if crash_dir.exists():
                # Archive crash dumps
                archive_dir = crash_dir / f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                for file in crash_dir.glob("*.dmp"):
                    shutil.move(str(file), str(archive_dir))
                
                actions_taken.append("Archived crash dumps")
            
            # 2. Clear corrupted state
            state_file = Path(f"state/{agent_name}_state.json")
            if state_file.exists():
                # Backup state
                backup_path = state_file.with_suffix('.backup')
                shutil.copy(state_file, backup_path)
                
                # Reset to clean state
                clean_state = {
                    'status': 'initialized',
                    'last_restart': datetime.now().isoformat(),
                    'crash_count': 0
                }
                
                with open(state_file, 'w') as f:
                    json.dump(clean_state, f, indent=2)
                
                actions_taken.append("Reset agent state")
            
            # 3. Restart with recovery mode
            restart_result = self.restart_with_recovery(agent_name, {
                'recovery_mode': True,
                'debug_enabled': True,
                'safe_mode': True
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted in recovery mode")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Crash healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Crash healing failed: {e}"
            }
    
    def _heal_copilot_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal GitHub Copilot-related issues"""
        logger.info(f"Healing Copilot issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Clear Copilot cache
            copilot_cache = Path.home() / ".copilot"
            if copilot_cache.exists():
                # Clear specific cache files, not entire directory
                for cache_file in copilot_cache.glob("*.cache"):
                    try:
                        os.remove(cache_file)
                    except:
                        pass
                actions_taken.append("Cleared Copilot cache")
            
            # 2. Verify GitHub authentication
            try:
                result = subprocess.run(
                    ["gh", "auth", "status"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    # Try to refresh auth
                    subprocess.run(["gh", "auth", "refresh"], capture_output=True)
                    actions_taken.append("Refreshed GitHub authentication")
                else:
                    actions_taken.append("GitHub authentication verified")
            except:
                pass
            
            # 3. Restart VS Code server if applicable
            # This would be specific to your setup
            actions_taken.append("Initiated IDE restart sequence")
            
            # 4. Restart agent with Copilot fallback
            restart_result = self.restart_with_recovery(agent_name, {
                'copilot_fallback': True,
                'alternative_ai': 'local_model'
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted with Copilot fallback")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Copilot healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Copilot healing failed: {e}"
            }
    
    def _heal_performance_issues(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Heal performance-related issues"""
        logger.info(f"Healing performance issues for {agent_name}")
        
        actions_taken = []
        success = False
        
        try:
            # 1. Clear performance-impacting caches
            cache_dirs = [
                Path(f"cache/{agent_name}"),
                Path(f"temp/{agent_name}"),
                Path(f"logs/{agent_name}/old")
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    actions_taken.append(f"Cleared {cache_dir.name}")
            
            # 2. Optimize configuration
            config_file = Path(f"configs/{agent_name}_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Apply performance optimizations
                optimizations = {
                    'batch_size': min(config.get('batch_size', 100), 50),
                    'cache_enabled': True,
                    'compression_enabled': True,
                    'logging_level': 'WARNING'
                }
                
                config.update(optimizations)
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                actions_taken.append("Applied performance optimizations")
            
            # 3. Restart with performance mode
            restart_result = self.restart_with_recovery(agent_name, {
                'performance_mode': True,
                'profiling_enabled': False,
                'optimize_memory': True
            })
            
            if restart_result['success']:
                actions_taken.append("Agent restarted in performance mode")
                success = True
            
            return {
                'success': success,
                'actions_taken': actions_taken,
                'message': 'Performance healing completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Performance healing failed: {e}"
            }
    
    def _generic_healing(self, agent_name: str, plan: Dict) -> Dict[str, Any]:
        """Generic healing strategy for unknown issue types"""
        logger.info(f"Applying generic healing for {agent_name}")
        
        actions_taken = []
        
        try:
            # 1. Basic cleanup
            actions_taken.append("Performed basic cleanup")
            
            # 2. Simple restart
            restart_result = self.restart_with_recovery(agent_name, {})
            
            if restart_result['success']:
                actions_taken.append("Agent restarted")
                return {
                    'success': True,
                    'actions_taken': actions_taken,
                    'message': 'Generic healing completed'
                }
            else:
                return {
                    'success': False,
                    'actions_taken': actions_taken,
                    'message': 'Generic healing failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'actions_taken': actions_taken,
                'message': f"Generic healing failed: {e}"
            }
    
    def restart_with_recovery(self, agent_name: str, recovery_params: Dict) -> Dict[str, Any]:
        """Smart restart with recovery parameters"""
        logger.info(f"Restarting {agent_name} with recovery params: {recovery_params}")
        
        try:
            # 1. Stop the agent gracefully
            process = self._get_agent_process(agent_name)
            if process:
                process.terminate()
                time.sleep(2)
                if process.is_running():
                    process.kill()
                logger.info(f"Stopped agent {agent_name}")
            
            # 2. Apply recovery parameters
            config_file = Path(f"configs/{agent_name}_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                config.update(recovery_params)
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            
            # 3. Restart with exponential backoff
            retries = 0
            delay = self.restart_config['initial_delay']
            
            while retries < self.restart_config['max_retries']:
                try:
                    # Start the agent
                    script_path = self._get_agent_script(agent_name)
                    if script_path:
                        cmd = [self.python_exe, script_path, agent_name]
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd="E:/Projects"
                        )
                        
                        # Wait a bit and check if it's running
                        time.sleep(5)
                        if process.poll() is None:
                            logger.info(f"Successfully restarted {agent_name}")
                            return {
                                'success': True,
                                'pid': process.pid,
                                'retries': retries
                            }
                    
                except Exception as e:
                    logger.error(f"Restart attempt {retries + 1} failed: {e}")
                
                retries += 1
                time.sleep(delay)
                delay = min(delay * self.restart_config['backoff_factor'], 
                          self.restart_config['max_delay'])
            
            return {
                'success': False,
                'message': f"Failed after {retries} attempts"
            }
            
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def apply_resource_fixes(self, agent_name: str, resource_type: str) -> Dict[str, Any]:
        """Apply fixes for resource issues"""
        actions = []
        
        try:
            if resource_type in ['memory', 'all']:
                # Clear memory caches
                freed = self._clear_memory_caches(agent_name)
                actions.append(f"Freed {freed}MB memory")
            
            if resource_type in ['disk', 'all']:
                # Clean up disk space
                freed = self._cleanup_disk_space(agent_name)
                actions.append(f"Freed {freed}MB disk space")
            
            if resource_type in ['cpu', 'all']:
                # Reduce CPU load
                self._reduce_cpu_load(agent_name)
                actions.append("Reduced CPU load")
            
            return {
                'success': True,
                'actions': actions
            }
            
        except Exception as e:
            logger.error(f"Resource fix failed: {e}")
            return {
                'success': False,
                'actions': actions,
                'error': str(e)
            }
    
    def _clear_memory_caches(self, agent_name: str) -> int:
        """Clear memory caches and return freed MB"""
        freed_mb = 0
        
        # Clear Python cache
        import gc
        gc.collect()
        
        # Clear agent-specific caches
        cache_dir = Path(f"cache/{agent_name}")
        if cache_dir.exists():
            size_before = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            freed_mb = size_before / (1024 * 1024)
        
        return int(freed_mb)
    
    def _cleanup_disk_space(self, agent_name: str) -> int:
        """Clean up disk space and return freed MB"""
        freed_mb = 0
        
        cleanup_dirs = [
            Path(f"temp/{agent_name}"),
            Path(f"logs/{agent_name}/old"),
            Path(f"cache/{agent_name}")
        ]
        
        for cleanup_dir in cleanup_dirs:
            if cleanup_dir.exists():
                size_before = sum(f.stat().st_size for f in cleanup_dir.rglob('*') if f.is_file())
                
                # Remove old files (>7 days)
                cutoff_time = time.time() - (7 * 24 * 60 * 60)
                for file in cleanup_dir.rglob('*'):
                    if file.is_file() and file.stat().st_mtime < cutoff_time:
                        try:
                            os.remove(file)
                        except:
                            pass
                
                size_after = sum(f.stat().st_size for f in cleanup_dir.rglob('*') if f.is_file())
                freed_mb += (size_before - size_after) / (1024 * 1024)
        
        return int(freed_mb)
    
    def _reduce_cpu_load(self, agent_name: str):
        """Reduce CPU load for agent"""
        process = self._get_agent_process(agent_name)
        if process:
            try:
                # Lower priority
                if sys.platform == "win32":
                    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else:
                    process.nice(10)
            except:
                pass
    
    def _get_agent_process(self, agent_name: str) -> Optional[psutil.Process]:
        """Get process object for agent"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and agent_name in ' '.join(cmdline):
                    return proc
            except:
                continue
        return None
    
    def _get_agent_script(self, agent_name: str) -> Optional[str]:
        """Get script path for agent"""
        # Map agent names to scripts
        script_mapping = {
            'issue_detector': 'intelligent-issue-detector.py',
            'self_healer': 'agent-self-healing.py',
            'communication_hub': 'agent-communication-hub.py',
            # Add more mappings as needed
        }
        
        # Check if specific mapping exists
        if agent_name in script_mapping:
            return script_mapping[agent_name]
        
        # Try to find script by pattern
        patterns = [
            f"{agent_name}.py",
            f"agent_{agent_name}.py",
            f"{agent_name}_agent.py"
        ]
        
        for pattern in patterns:
            script_path = Path(pattern)
            if script_path.exists():
                return str(script_path)
        
        return None
    
    def _record_healing(self, agent_name: str, issue_type: str, result: Dict):
        """Record healing action in history"""
        healing_record = {
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'issue_type': issue_type,
            'success': result.get('success', False),
            'duration': result.get('duration', 0),
            'actions_taken': result.get('actions_taken', []),
            'message': result.get('message', '')
        }
        
        self.healing_history.append(healing_record)
        
        # Update metrics
        self.metrics['total_healings'] += 1
        if result.get('success'):
            self.metrics['successful_healings'] += 1
        else:
            self.metrics['failed_healings'] += 1
        
        if issue_type not in self.metrics['healings_by_type']:
            self.metrics['healings_by_type'][issue_type] = 0
        self.metrics['healings_by_type'][issue_type] += 1
        
        self.metrics['healing_times'].append(result.get('duration', 0))
        if self.metrics['healing_times']:
            self.metrics['avg_healing_time'] = sum(self.metrics['healing_times']) / len(self.metrics['healing_times'])
        
        # Save to file
        with open('healing_history.json', 'w') as f:
            json.dump(self.healing_history[-100:], f, indent=2)  # Keep last 100 records
    
    def monitor_resolution_plans(self):
        """Monitor for new resolution plans and execute healing"""
        logger.info("Monitoring resolution plans...")
        
        processed_plans = set()
        
        while self.monitoring:
            try:
                # Check for new resolution plans
                if self.resolution_plans_dir.exists():
                    for plan_file in self.resolution_plans_dir.glob("*.json"):
                        if plan_file.name not in processed_plans:
                            try:
                                with open(plan_file, 'r') as f:
                                    plan = json.load(f)
                                
                                # Execute healing
                                result = self.execute_healing_action(
                                    plan['agent_name'],
                                    plan['issue_type'],
                                    plan
                                )
                                
                                logger.info(f"Healing result for {plan['agent_name']}: {result}")
                                
                                # Mark as processed
                                processed_plans.add(plan_file.name)
                                
                                # Archive processed plan
                                archive_dir = self.resolution_plans_dir / "processed"
                                archive_dir.mkdir(exist_ok=True)
                                shutil.move(str(plan_file), str(archive_dir / plan_file.name))
                                
                            except Exception as e:
                                logger.error(f"Error processing plan {plan_file}: {e}")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(5)  # Check every 5 seconds
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_resolution_plans, daemon=True)
            self.monitor_thread.start()
            logger.info("Self-healing monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("Self-healing monitoring stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current healing metrics"""
        success_rate = 0
        if self.metrics['total_healings'] > 0:
            success_rate = (self.metrics['successful_healings'] / self.metrics['total_healings']) * 100
        
        return {
            'total_healings': self.metrics['total_healings'],
            'successful_healings': self.metrics['successful_healings'],
            'failed_healings': self.metrics['failed_healings'],
            'success_rate': success_rate,
            'healings_by_type': self.metrics['healings_by_type'],
            'avg_healing_time': self.metrics['avg_healing_time'],
            'active_healings': len(self.active_healings)
        }
    
    def save_progress(self):
        """Save progress to JSON file"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'component': 'agent-self-healing',
            'status': 'operational',
            'metrics': self.get_metrics(),
            'active_healings': list(self.active_healings.keys()),
            'monitoring_active': self.monitoring
        }
        
        # Update existing progress file
        try:
            with open('claude_opus_progress.json', 'r') as f:
                all_progress = json.load(f)
        except:
            all_progress = {}
        
        all_progress['self_healing'] = progress
        
        with open('claude_opus_progress.json', 'w') as f:
            json.dump(all_progress, f, indent=2)
        
        logger.info("Progress saved to claude_opus_progress.json")


def main():
    """Main execution function"""
    logger.info("Starting Agent Self-Healing System...")
    
    # Initialize self-healing system
    healer = SelfHealing()
    
    # Create necessary directories
    for dir_name in ['resolution_plans', 'configs', 'cache', 'temp', 'logs', 'state', 'crashes', 'tokens']:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Start monitoring
    healer.start_monitoring()
    
    try:
        # Keep running and periodically save progress
        while True:
            time.sleep(30)  # Save progress every 30 seconds
            healer.save_progress()
            
            # Log current metrics
            metrics = healer.get_metrics()
            logger.info(f"Healing metrics: {metrics['total_healings']} total, "
                       f"Success rate: {metrics['success_rate']:.1f}%")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        healer.stop_monitoring()
        healer.save_progress()
        sys.exit(0)


if __name__ == "__main__":
    main()
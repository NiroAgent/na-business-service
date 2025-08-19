#!/usr/bin/env python3
"""
Activity Monitor Agent - Tracks actual work being done across all services
"""

import subprocess
import json
from datetime import datetime, timedelta
from collections import defaultdict

class ActivityMonitorAgent:
    """Monitor and report on actual development activity"""
    
    def __init__(self):
        self.repos = {
            'NiroSubs': [
                'NiroSubs-V2/ns-auth',
                'NiroSubs-V2/ns-dashboard',
                'NiroSubs-V2/ns-payments',
                'NiroSubs-V2/ns-user',
                'NiroSubs-V2/ns-shell'
            ],
            'VisualForge': [
                'VisualForgeMediaV2/vf-auth-service',
                'VisualForgeMediaV2/vf-dashboard-service',
                'VisualForgeMediaV2/vf-video-service',
                'VisualForgeMediaV2/vf-image-service',
                'VisualForgeMediaV2/vf-audio-service',
                'VisualForgeMediaV2/vf-text-service',
                'VisualForgeMediaV2/vf-bulk-service'
            ],
            'Operations': [
                'VisualForgeMediaV2/business-operations'
            ]
        }
        
        self.activity_data = defaultdict(lambda: {
            'open_issues': 0,
            'closed_issues': 0,
            'stalled_issues': 0,
            'active_issues': 0,
            'comments_today': 0,
            'commits_today': 0,
            'prs_open': 0,
            'oldest_issue_days': 0,
            'efficiency_score': 0
        })
        
    def generate_activity_report(self):
        """Generate comprehensive activity report"""
        
        print("\n" + "="*80)
        print("ACTIVITY MONITORING REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Collect data for all repos
        for category, repos in self.repos.items():
            print(f"\n[{category.upper()}]")
            for repo in repos:
                self.analyze_repo_activity(repo)
                
        # Generate summary
        self.generate_summary()
        
        # Identify problems
        self.identify_problems()
        
        # Generate recommendations
        self.generate_recommendations()
        
    def analyze_repo_activity(self, repo: str):
        """Analyze activity for a single repository"""
        
        service = repo.split('/')[-1]
        data = self.activity_data[service]
        
        # Get open issues
        result = subprocess.run([
            'gh', 'issue', 'list',
            '--repo', repo,
            '--state', 'open',
            '--json', 'number,title,createdAt,updatedAt,comments',
            '--limit', '100'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            data['open_issues'] = len(issues)
            
            # Analyze each issue
            now = datetime.now()
            for issue in issues:
                created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(issue['updatedAt'].replace('Z', '+00:00'))
                
                # Check if stalled (no update in 3 days)
                days_since_update = (now - updated.replace(tzinfo=None)).days
                if days_since_update > 3:
                    data['stalled_issues'] += 1
                elif days_since_update <= 1:
                    data['active_issues'] += 1
                    
                # Track oldest issue
                days_old = (now - created.replace(tzinfo=None)).days
                data['oldest_issue_days'] = max(data['oldest_issue_days'], days_old)
                
                # Count recent comments
                for comment in issue.get('comments', []):
                    comment_date = datetime.fromisoformat(comment.get('createdAt', '').replace('Z', '+00:00'))
                    if (now - comment_date.replace(tzinfo=None)).days == 0:
                        data['comments_today'] += 1
        
        # Get closed issues (last 7 days)
        result = subprocess.run([
            'gh', 'issue', 'list',
            '--repo', repo,
            '--state', 'closed',
            '--limit', '50'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            closed_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            data['closed_issues'] = closed_count
            
        # Get open PRs
        result = subprocess.run([
            'gh', 'pr', 'list',
            '--repo', repo,
            '--state', 'open',
            '--json', 'number'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            prs = json.loads(result.stdout)
            data['prs_open'] = len(prs)
            
        # Calculate efficiency score
        if data['open_issues'] > 0:
            data['efficiency_score'] = int(
                (data['active_issues'] / data['open_issues'] * 50) +
                (data['closed_issues'] / max(1, data['open_issues']) * 30) +
                (20 if data['stalled_issues'] == 0 else 10 - data['stalled_issues'])
            )
        
        # Print repo summary
        self.print_repo_summary(service, data)
        
    def print_repo_summary(self, service: str, data: dict):
        """Print summary for a single repo"""
        
        # Determine status emoji/indicator
        if data['efficiency_score'] >= 70:
            status = "[ACTIVE]"
        elif data['efficiency_score'] >= 40:
            status = "[SLOW]"
        elif data['open_issues'] == 0:
            status = "[EMPTY]"
        else:
            status = "[STALLED]"
            
        print(f"\n  {service} {status}")
        print(f"    Open: {data['open_issues']} | Closed: {data['closed_issues']} | Stalled: {data['stalled_issues']}")
        print(f"    Activity: {data['comments_today']} comments today | {data['prs_open']} open PRs")
        
        if data['oldest_issue_days'] > 7:
            print(f"    ⚠️  Oldest issue: {data['oldest_issue_days']} days old")
        
        if data['stalled_issues'] > 0:
            print(f"    ⚠️  {data['stalled_issues']} issues have no recent activity")
            
    def generate_summary(self):
        """Generate overall summary"""
        
        print("\n" + "="*80)
        print("OVERALL SUMMARY")
        print("="*80)
        
        total_open = sum(d['open_issues'] for d in self.activity_data.values())
        total_closed = sum(d['closed_issues'] for d in self.activity_data.values())
        total_stalled = sum(d['stalled_issues'] for d in self.activity_data.values())
        total_active = sum(d['active_issues'] for d in self.activity_data.values())
        total_comments = sum(d['comments_today'] for d in self.activity_data.values())
        
        print(f"\nTotal Issues: {total_open} open, {total_closed} recently closed")
        print(f"Activity Status: {total_active} active, {total_stalled} stalled")
        print(f"Today's Activity: {total_comments} comments")
        
        # Calculate overall health
        if total_open > 0:
            stall_rate = (total_stalled / total_open) * 100
            activity_rate = (total_active / total_open) * 100
            
            print(f"\nHealth Metrics:")
            print(f"  Stall Rate: {stall_rate:.1f}% (target: <20%)")
            print(f"  Activity Rate: {activity_rate:.1f}% (target: >50%)")
            
            if stall_rate > 50:
                print("  ⚠️  CRITICAL: Over 50% of issues are stalled!")
            elif stall_rate > 30:
                print("  ⚠️  WARNING: High stall rate detected")
                
    def identify_problems(self):
        """Identify specific problems"""
        
        print("\n" + "="*80)
        print("PROBLEMS DETECTED")
        print("="*80)
        
        problems = []
        
        for service, data in self.activity_data.items():
            # Check for abandoned services
            if data['open_issues'] > 0 and data['active_issues'] == 0:
                problems.append(f"❌ {service}: No active work (all issues stalled)")
                
            # Check for bottlenecks
            if data['open_issues'] > 10 and data['closed_issues'] == 0:
                problems.append(f"❌ {service}: Bottleneck - {data['open_issues']} open, none closed")
                
            # Check for old issues
            if data['oldest_issue_days'] > 14:
                problems.append(f"⚠️  {service}: Has issues over 2 weeks old")
                
            # Check for no QA activity
            if 'QA' in str(data) and data['comments_today'] == 0:
                problems.append(f"⚠️  {service}: No QA activity today")
                
        if problems:
            for problem in problems:
                print(f"\n  {problem}")
        else:
            print("\n  ✅ No critical problems detected")
            
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        # Analyze patterns
        total_stalled = sum(d['stalled_issues'] for d in self.activity_data.values())
        total_open = sum(d['open_issues'] for d in self.activity_data.values())
        
        if total_stalled > 10:
            recommendations.append("1. URGENT: Review and restart {total_stalled} stalled issues")
            recommendations.append("   - Assign active agents to stalled work")
            recommendations.append("   - Close issues that are no longer needed")
            
        # Check for imbalanced workload
        workloads = [(s, d['open_issues']) for s, d in self.activity_data.items()]
        workloads.sort(key=lambda x: x[1], reverse=True)
        
        if workloads[0][1] > 20 and workloads[-1][1] < 5:
            recommendations.append("2. REBALANCE: Redistribute work from overloaded services")
            recommendations.append(f"   - {workloads[0][0]} has {workloads[0][1]} issues")
            recommendations.append(f"   - {workloads[-1][0]} has only {workloads[-1][1]} issues")
            
        # Check for missing processes
        no_prs = [s for s, d in self.activity_data.items() if d['prs_open'] == 0 and d['open_issues'] > 5]
        if no_prs:
            recommendations.append("3. PROCESS: These services have work but no PRs:")
            for service in no_prs[:3]:
                recommendations.append(f"   - {service}: Create PRs for completed work")
                
        # Agent recommendations
        if total_stalled > total_open * 0.3:
            recommendations.append("4. AGENTS: Deploy more developer agents")
            recommendations.append("   - Current agents may be overloaded")
            recommendations.append("   - Consider scaling up spot instances")
            
        for rec in recommendations:
            print(f"\n{rec}")
            
    def create_efficiency_dashboard(self):
        """Create efficiency metrics dashboard"""
        
        print("\n" + "="*80)
        print("EFFICIENCY DASHBOARD")
        print("="*80)
        
        # Calculate metrics
        services_data = []
        for service, data in self.activity_data.items():
            if data['open_issues'] > 0:
                velocity = data['closed_issues'] / max(1, data['open_issues'])
                services_data.append({
                    'service': service,
                    'velocity': velocity,
                    'efficiency': data['efficiency_score'],
                    'open': data['open_issues'],
                    'stalled': data['stalled_issues']
                })
                
        # Sort by efficiency
        services_data.sort(key=lambda x: x['efficiency'], reverse=True)
        
        print("\nTop Performers:")
        for item in services_data[:3]:
            print(f"  ✅ {item['service']}: {item['efficiency']}% efficiency")
            
        print("\nNeeds Attention:")
        for item in services_data[-3:]:
            if item['efficiency'] < 50:
                print(f"  ⚠️  {item['service']}: {item['efficiency']}% efficiency")
                
        # Overall metrics
        avg_efficiency = sum(d['efficiency'] for d in services_data) / max(1, len(services_data))
        print(f"\nOverall Efficiency: {avg_efficiency:.1f}%")
        
        if avg_efficiency < 40:
            print("⚠️  CRITICAL: System efficiency below 40%")
        elif avg_efficiency < 60:
            print("⚠️  WARNING: System efficiency could be improved")
        else:
            print("✅ System operating efficiently")


def main():
    """Main entry point"""
    
    monitor = ActivityMonitorAgent()
    
    print("\n[START] Activity Monitoring System")
    
    # Generate full report
    monitor.generate_activity_report()
    
    # Create efficiency dashboard
    monitor.create_efficiency_dashboard()
    
    print("\n" + "="*80)
    print("[COMPLETE] Monitoring Report Generated")
    print("="*80)
    
    # Create monitoring issue if problems found
    total_stalled = sum(d['stalled_issues'] for d in monitor.activity_data.values())
    if total_stalled > 5:
        print("\n[ACTION] Creating urgent issue for stalled work...")
        
        body = f"""## URGENT: {total_stalled} Issues Are Stalled

The activity monitor has detected that {total_stalled} issues across all services have had no activity for >3 days.

### Services Affected:
"""
        for service, data in monitor.activity_data.items():
            if data['stalled_issues'] > 0:
                body += f"- {service}: {data['stalled_issues']} stalled issues\n"
                
        body += """
### Required Actions:
1. Review all stalled issues
2. Reassign to active agents
3. Close any obsolete issues
4. Add progress updates

### Priority: P0
This is blocking overall system progress.

assigned_agent: vf-manager-agent
type: escalation
"""
        
        subprocess.run([
            'gh', 'issue', 'create',
            '--repo', 'VisualForgeMediaV2/business-operations',
            '--title', f'[URGENT] {total_stalled} Stalled Issues Need Attention',
            '--body', body
        ], capture_output=True)
        
        print("[OK] Escalation issue created")


if __name__ == '__main__':
    main()
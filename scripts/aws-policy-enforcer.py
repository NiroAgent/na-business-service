#!/usr/bin/env python3
"""
AWS Backend Processing Policy Enforcement
Validates that all AI agents comply with the serverless-first policy
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class PolicyEnforcer:
    def __init__(self):
        self.policy_violations = []
        self.compliance_score = 0
        self.agents_checked = []
        
        # Load the policy requirements
        self.policy_requirements = {
            "aws_backend_hierarchy": [
                "AWS Lambda",
                "AWS Fargate Tasks", 
                "AWS Fargate Container Service",
                "EC2"
            ],
            "mandatory_capabilities": [
                "serverless deployment",
                "auto-scaling",
                "scale-to-zero",
                "cost optimization"
            ],
            "prohibited_patterns": [
                "always-on EC2 without justification",
                "fixed-size instances",
                "manual scaling"
            ]
        }
    
    def check_agent_compliance(self, agent_file: str) -> Dict[str, Any]:
        """Check if an agent file complies with the AWS backend policy"""
        compliance_result = {
            "agent": agent_file,
            "compliant": False,
            "policy_found": False,
            "violations": [],
            "recommendations": []
        }
        
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if AWS backend policy is implemented
            if "aws_backend_policy" in content.lower():
                compliance_result["policy_found"] = True
                
                # Check for priority order
                if "lambda" in content.lower() and "fargate" in content.lower():
                    compliance_result["compliant"] = True
                else:
                    compliance_result["violations"].append("Missing Lambda/Fargate prioritization")
                
                # Check for serverless patterns
                serverless_patterns = ["serverless", "scale to zero", "auto-scaling"]
                found_patterns = sum(1 for pattern in serverless_patterns if pattern in content.lower())
                
                if found_patterns < 2:
                    compliance_result["violations"].append("Insufficient serverless patterns")
                
                # Check for prohibited patterns
                prohibited = ["always-on ec2", "fixed instance", "manual scaling"]
                for pattern in prohibited:
                    if pattern in content.lower():
                        compliance_result["violations"].append(f"Prohibited pattern found: {pattern}")
            else:
                compliance_result["violations"].append("AWS Backend Policy not implemented")
                compliance_result["recommendations"].append("Add aws_backend_policy to agent initialization")
            
            # Final compliance check
            if compliance_result["policy_found"] and len(compliance_result["violations"]) == 0:
                compliance_result["compliant"] = True
                
        except Exception as e:
            compliance_result["violations"].append(f"Error reading file: {str(e)}")
        
        return compliance_result
    
    def audit_all_agents(self) -> Dict[str, Any]:
        """Audit all AI agents for policy compliance"""
        print("🔍 AWS BACKEND PROCESSING POLICY AUDIT")
        print("=" * 50)
        
        # Find all AI agent files
        agent_files = [
            "ai-architect-agent.py",
            "ai-developer-agent.py", 
            "ai-qa-agent.py",
            "ai-devops-agent.py"
        ]
        
        audit_results = []
        total_compliant = 0
        
        for agent_file in agent_files:
            if os.path.exists(agent_file):
                print(f"\n📋 Checking {agent_file}...")
                result = self.check_agent_compliance(agent_file)
                audit_results.append(result)
                
                if result["compliant"]:
                    print(f"  ✅ COMPLIANT")
                    total_compliant += 1
                else:
                    print(f"  ❌ NON-COMPLIANT")
                    for violation in result["violations"]:
                        print(f"    • {violation}")
                
                self.agents_checked.append(agent_file)
            else:
                print(f"\n⚠️  {agent_file} not found")
        
        # Calculate compliance score
        compliance_percentage = (total_compliant / len(agent_files)) * 100 if agent_files else 0
        
        # Generate final report
        final_report = {
            "audit_timestamp": datetime.now().isoformat(),
            "total_agents": len(agent_files),
            "agents_found": len([r for r in audit_results if os.path.exists(r["agent"])]),
            "compliant_agents": total_compliant,
            "compliance_percentage": compliance_percentage,
            "policy_status": "ENFORCED" if compliance_percentage == 100 else "VIOLATIONS_FOUND",
            "detailed_results": audit_results
        }
        
        print("\n" + "=" * 50)
        print("📊 AUDIT SUMMARY")
        print("=" * 50)
        print(f"Total Agents: {final_report['total_agents']}")
        print(f"Agents Found: {final_report['agents_found']}")
        print(f"Compliant Agents: {final_report['compliant_agents']}")
        print(f"Compliance Rate: {compliance_percentage:.1f}%")
        print(f"Policy Status: {final_report['policy_status']}")
        
        if compliance_percentage == 100:
            print("\n🎉 ALL AGENTS ARE COMPLIANT WITH AWS BACKEND POLICY!")
        else:
            print(f"\n⚠️  POLICY VIOLATIONS DETECTED - REMEDIATION REQUIRED")
        
        # Save audit report
        report_file = f"policy_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print(f"\n📄 Detailed audit report saved: {report_file}")
        
        return final_report
    
    def generate_compliance_instructions(self) -> str:
        """Generate instructions for bringing agents into compliance"""
        instructions = """
🚀 AWS BACKEND PROCESSING POLICY COMPLIANCE INSTRUCTIONS

To ensure all agents comply with the serverless-first policy:

1. ADD POLICY TO AGENT INITIALIZATION:
   ```python
   self.aws_backend_policy = {
       "priority_order": [
           "AWS Lambda (serverless functions)",
           "AWS Fargate Tasks (Batch/Step Functions)", 
           "AWS Fargate Container Service (ECS/EKS)",
           "EC2 (requires justification)"
       ],
       "objectives": [
           "Scale to zero when idle",
           "Infinite auto-scaling capability", 
           "Cost optimization - pay for usage only"
       ]
   }
   ```

2. UPDATE CAPABILITIES:
   - Add "serverless_deployment" 
   - Add "auto_scaling_config"
   - Add "cost_optimization"

3. IMPLEMENT DECISION LOGIC:
   - Default to Lambda for all APIs
   - Use Fargate Batch for long-running jobs
   - Require justification for EC2 usage

4. VALIDATE IN QA:
   - Test scale-to-zero behavior
   - Validate auto-scaling performance
   - Check cost optimization

5. DEPLOY WITH SERVERLESS TOOLS:
   - Use AWS SAM/CDK for Lambda
   - Use Terraform for infrastructure
   - Implement monitoring and alerting

COMPLIANCE IS MANDATORY FOR ALL AGENTS!
        """
        return instructions

if __name__ == "__main__":
    enforcer = PolicyEnforcer()
    audit_result = enforcer.audit_all_agents()
    
    if audit_result["compliance_percentage"] < 100:
        print(enforcer.generate_compliance_instructions())

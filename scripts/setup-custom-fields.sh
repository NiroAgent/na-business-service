#!/bin/bash
# Custom Fields Setup for PM Integration

echo 'Setting up custom fields for PM integration...'

gh api "repos/NiroAgentV2/autonomous-business-system/properties/values" -X PATCH -f properties='[{"property_name": "assigned_agent", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/autonomous-business-system/properties/values" -X PATCH -f properties='[{"property_name": "agent_status", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/autonomous-business-system/properties/values" -X PATCH -f properties='[{"property_name": "priority_level", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/autonomous-business-system/properties/values" -X PATCH -f properties='[{"property_name": "pm_approved", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/agent-dashboard/properties/values" -X PATCH -f properties='[{"property_name": "assigned_agent", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/agent-dashboard/properties/values" -X PATCH -f properties='[{"property_name": "agent_status", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/agent-dashboard/properties/values" -X PATCH -f properties='[{"property_name": "priority_level", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/agent-dashboard/properties/values" -X PATCH -f properties='[{"property_name": "pm_approved", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/business-operations/properties/values" -X PATCH -f properties='[{"property_name": "assigned_agent", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/business-operations/properties/values" -X PATCH -f properties='[{"property_name": "agent_status", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/business-operations/properties/values" -X PATCH -f properties='[{"property_name": "priority_level", "value": "unassigned"}]'
gh api "repos/NiroAgentV2/business-operations/properties/values" -X PATCH -f properties='[{"property_name": "pm_approved", "value": "unassigned"}]'

echo 'Custom fields setup complete!'

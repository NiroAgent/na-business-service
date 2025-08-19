#!/bin/bash

# Dashboard Enhancement Stories - Auto Assignment Script
# Creates GitHub issues for PM with detailed enhancement specifications

echo "📋 Creating Dashboard Enhancement Stories for PM..."

# Story 1: Environment-Specific Cost Breakdown
echo "🏗️ Creating Cost Breakdown Enhancement Story..."

gh issue create \
  --title "📊 Dashboard Enhancement: Environment-Specific Cost Breakdown" \
  --body "$(cat /e/Projects/stories/dashboard-cost-breakdown-enhancement.md)" \
  --label "enhancement,dashboard,cost-optimization,high-priority" \
  --assignee "@product-manager" \
  --milestone "Dashboard Enhancements Epic"

if [ $? -eq 0 ]; then
    echo "✅ Cost Breakdown Story created successfully"
else
    echo "⚠️ Cost Breakdown Story creation failed - will create manually"
fi

# Story 2: Real-Time Console Grid View  
echo "🖥️ Creating Console Grid Enhancement Story..."

gh issue create \
  --title "🖥️ Dashboard Enhancement: Real-Time Console Grid View" \
  --body "$(cat /e/Projects/stories/dashboard-console-grid-enhancement.md)" \
  --label "enhancement,dashboard,real-time,critical-priority" \
  --assignee "@product-manager" \
  --milestone "Dashboard Enhancements Epic"

if [ $? -eq 0 ]; then
    echo "✅ Console Grid Story created successfully"
else
    echo "⚠️ Console Grid Story creation failed - will create manually"
fi

# Story 3: Interactive Console Debugging
echo "🔍 Creating Interactive Debugging Enhancement Story..."

gh issue create \
  --title "🔍 Dashboard Enhancement: Interactive Console Debugging" \
  --body "$(cat /e/Projects/stories/dashboard-interactive-debugging-enhancement.md)" \
  --label "enhancement,dashboard,debugging,interactive,high-priority" \
  --assignee "@product-manager" \
  --milestone "Dashboard Enhancements Epic"

if [ $? -eq 0 ]; then
    echo "✅ Interactive Debugging Story created successfully"
else
    echo "⚠️ Interactive Debugging Story creation failed - will create manually"
fi

# Epic Summary for PM
echo "📋 Creating Epic Summary for PM..."

gh issue create \
  --title "📋 EPIC: Advanced Dashboard Monitoring & Cost Management" \
  --body "$(cat /e/Projects/stories/dashboard-enhancement-epic-summary.md)" \
  --label "epic,dashboard,cost-management,monitoring,pm-review" \
  --assignee "@product-manager"

if [ $? -eq 0 ]; then
    echo "✅ Epic Summary created successfully"
else
    echo "⚠️ Epic Summary creation failed - will create manually"
fi

echo ""
echo "🎯 DASHBOARD ENHANCEMENT STORIES SUMMARY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Story 1: Environment Cost Breakdown (8 points)"
echo "   • Cost breakdown by environment (Dev/Staging/Prod)"
echo "   • Interactive charts with optimization recommendations"
echo "   • 30-day trends and budget variance tracking"
echo ""
echo "🖥️ Story 2: Real-Time Console Grid (13 points)"
echo "   • Live grid view of all 50+ agent consoles"
echo "   • WebSocket streaming with <500ms latency"
echo "   • Advanced filtering and search capabilities"
echo ""
echo "🔍 Story 3: Interactive Console Debugging (21 points)"
echo "   • Full-screen console with interactive feedback"
echo "   • Context-aware assistance and knowledge base"
echo "   • Human guidance integration for stuck agents"
echo ""
echo "📋 Epic Summary: 42 total story points (3-4 sprints)"
echo "   • 10% additional cost savings expected"
echo "   • 50% faster issue resolution"
echo "   • 99.9% monitoring uptime target"
echo ""
echo "🎯 PM ACTION REQUIRED:"
echo "   1. Review and prioritize stories"
echo "   2. Assign development team"
echo "   3. Approve AWS Cost Explorer API integration"
echo "   4. Confirm 3-4 sprint timeline"
echo "   5. Define success metrics and KPIs"
echo ""
echo "📁 Story Files Created:"
echo "   • /e/Projects/stories/dashboard-cost-breakdown-enhancement.md"
echo "   • /e/Projects/stories/dashboard-console-grid-enhancement.md" 
echo "   • /e/Projects/stories/dashboard-interactive-debugging-enhancement.md"
echo "   • /e/Projects/stories/dashboard-enhancement-epic-summary.md"
echo ""
echo "✅ All enhancement stories ready for PM review and sprint planning!"

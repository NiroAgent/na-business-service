#!/bin/bash
# GitHub App Installation Script for AI Agents

echo "Setting up GitHub App for AI Agents..."

# 1. Create GitHub App
echo "Creating GitHub App..."
gh api /app-manifests/$(gh api /user --jq .login)/conversions \
  --input manifest.json \
  --jq '.id' > app_id.txt

APP_ID=$(cat app_id.txt)
echo "Created App ID: $APP_ID"

# 2. Generate installation token
echo "Generating installation token..."
gh api /app/installations \
  -H "Accept: application/vnd.github.v3+json" \
  --jq '.[0].id' > installation_id.txt

INSTALLATION_ID=$(cat installation_id.txt)

# 3. Install app on all repos
REPOS=(
    "vf-dashboard-service"
    "vf-auth-service"
    "vf-video-service"
    "vf-image-service"
    "vf-audio-service"
    "vf-text-service"
    "business-operations"
)

for repo in "${REPOS[@]}"; do
    echo "Installing app on $repo..."
    gh api /user/installations/$INSTALLATION_ID/repositories/$repo \
      -X PUT \
      -H "Accept: application/vnd.github.v3+json"
done

echo "GitHub App setup complete!"

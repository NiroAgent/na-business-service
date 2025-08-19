# NA Dashboard

NiroAgent Dashboard - Real-time AWS infrastructure monitoring and cost analysis

## 🏗️ Architecture

This is a microservices-based dashboard built with:

- **Backend API**: Node.js TypeScript Lambda with Express.js
- **Frontend**: Vite React with TypeScript  
- **Infrastructure**: AWS CloudFormation + GitHub Actions
- **Real-time**: WebSocket connections for live updates
- **Monitoring**: EC2, CloudWatch, Cost Explorer integration

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Docker & Docker Compose
- AWS CLI configured
- Access to VF AWS accounts (dev: 319040880702, staging: 275057778147, production: 229742714212)

### Local Development

```bash
# Clone and install dependencies
cd na-dashboard
npm install

# Start backend API (runs on localhost:4000)
cd services/dashboard-api
npm run dev

# Start frontend (runs on localhost:3001)  
cd services/dashboard-mfe
npm run dev

# Open dashboard
# Visit http://localhost:3001 in your browser
```

The dashboard works in **demo mode** by default with simulated AWS data when real AWS credentials are not configured.

### Environment Variables

Create `.env` files in each service directory:

```bash
# services/dashboard-api/.env
NODE_ENV=development
PORT=4000
AWS_REGION=us-east-1
FRONTEND_URL=http://localhost:3000

# services/dashboard-mfe/.env
VITE_API_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000
```

## 📦 Project Structure

```
na-dashboard/
├── services/                  # Microservices
│   ├── dashboard-api/        # Node.js TypeScript API
│   │   ├── src/
│   │   │   ├── na-dashboard-server.ts  # Main server with AWS integration
│   │   │   ├── routes/                 # API routes (aws, cost, monitoring)
│   │   │   └── server.ts               # Legacy server file
│   │   ├── .env                        # Environment configuration
│   │   ├── Dockerfile
│   │   └── package.json
│   └── dashboard-mfe/        # React TypeScript frontend
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── pages/        # Page components
│       │   ├── App.tsx       # Main app
│       │   └── ...
│       ├── Dockerfile
│       └── package.json
├── packages/                 # Shared packages
│   └── shared-types/         # TypeScript type definitions
├── infrastructure/          # Infrastructure as Code
│   └── aws/                 # CloudFormation templates
├── .github/workflows/       # CI/CD pipelines
└── docker-compose.yml       # Local development
```

## 🛠️ Development

### API Development

```bash
cd services/dashboard-api
npm run dev          # Start with hot reload
npm run build        # Build TypeScript
npm run test         # Run tests
npm run lint         # ESLint
```

### Frontend Development

```bash
cd services/dashboard-mfe  
npm run dev          # Start Vite dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm test             # Run Vitest tests
```

### Shared Types

```bash
cd packages/shared-types
npm run build        # Build TypeScript definitions
npm run dev          # Watch mode
```

## 🌐 API Endpoints

### AWS Routes (`/api/aws`)
- `GET /instances` - All EC2 instances across environments
- `GET /instances/:environment` - Instances for specific environment
- `GET /metrics/:environment/:instanceId` - CloudWatch metrics
- `GET /regions` - Available AWS regions

### Cost Routes (`/api/cost`)
- `GET /breakdown` - Cost breakdown across all environments
- `GET /breakdown/:environment` - Cost breakdown for specific environment  
- `GET /trends/:environment` - Cost trends over time

### Monitoring Routes (`/api/monitoring`)
- `GET /status` - Real-time monitoring status
- `GET /alerts/:environment?` - Alerts for environment
- `POST /start` - Start real-time monitoring
- `POST /stop` - Stop real-time monitoring
- `GET /stream` - Server-sent events stream

## 🔄 Real-time Features

### WebSocket Connection
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:4000/ws')

// Subscribe to updates
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'instances'
}))
```

### Message Types
- `connected` - Initial connection
- `alert` - New alerts
- `status-update` - Real-time status updates
- `monitoring-started/stopped` - Monitoring state changes

## 🚢 Deployment

### Environments

| Environment | Account | Branch | URL |
|-------------|---------|---------|-----|
| Development | 319040880702 | `development` | https://na-dashboard-dev.example.com |
| Staging | 275057778147 | `release/*` | https://na-dashboard-staging.example.com |
| Production | 229742714212 | `main` | https://na-dashboard.example.com |

### Deployment Process

1. **Push to branch** triggers GitHub Actions
2. **Build & Test** - Dependencies, linting, type checking
3. **Docker Images** - Build and push to ECR
4. **Infrastructure** - Deploy CloudFormation stack
5. **Notification** - Comment on PR with deployment info

### Manual Deployment

```bash
# Deploy to development
aws cloudformation deploy \
  --template-file infrastructure/aws/dashboard-infrastructure.yaml \
  --stack-name na-dashboard-development \
  --parameter-overrides Environment=development \
  --capabilities CAPABILITY_NAMED_IAM

# Build and deploy locally
npm run build
npm run deploy
```

## 🔐 AWS Permissions

Required IAM permissions for dashboard functionality:

### Cross-Account Roles
- `CrossAccountDashboardRole` in each target account
- Permissions: EC2 read, CloudWatch read, Cost Explorer read
- Trust relationship with GitHub Actions role

### GitHub Actions Role
- `GitHubActionsRole` in deployment accounts
- Permissions: ECR push, CloudFormation deploy, assume cross-account roles

## 📊 Monitoring & Observability

### Health Checks
- `/health` - Basic API health
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe

### Metrics Collected
- EC2 instance counts by environment
- CPU utilization trends
- Cost breakdown by service
- Alert counts and status

### Logging
- Structured JSON logs
- AWS CloudWatch integration
- Real-time log streaming

## 🧪 Testing

```bash
# Run all tests
npm test

# API tests
cd services/dashboard-api && npm test

# Frontend tests  
cd services/dashboard-mfe && npm test

# E2E tests (if configured)
npm run test:e2e
```

## 🤝 Contributing

1. Create feature branch from `development`
2. Make changes following coding standards
3. Add tests for new functionality
4. Submit PR to `development` branch
5. Automated tests and deployment to dev environment
6. Code review and merge

### Coding Standards
- TypeScript for all code
- ESLint + Prettier for formatting
- Conventional commits
- 100% type coverage target

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/niroagent/na-dashboard/issues)
- **Documentation**: [Wiki](https://github.com/niroagent/na-dashboard/wiki)
- **Slack**: #na-dashboard channel

## 🎯 Roadmap

- [ ] Multi-region support
- [ ] Custom metrics dashboards  
- [ ] Cost optimization recommendations
- [ ] Automated alerting rules
- [ ] Mobile responsive design
- [ ] Export capabilities (PDF, Excel)
- [ ] Historical data retention
- [ ] SSO integration

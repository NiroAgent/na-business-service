# VisualForge Media Types, Database Interfaces, SDK & Secrets Management Analysis

## Overview

This document provides comprehensive details about the shared types library (vf-media-types), database interfaces, SDK patterns, and secrets management across both NiroSubs-V2 and VisualForgeMediaV2 projects.

## Table of Contents

1. [VF-Media-Types Package](#vf-media-types-package)
2. [Database Interface Patterns](#database-interface-patterns)
3. [SDK Architecture (VF-Utils)](#sdk-architecture-vf-utils)
4. [Secrets Management](#secrets-management)
5. [Cross-Project Integration](#cross-project-integration)
6. [Implementation Recommendations](#implementation-recommendations)

---

## VF-Media-Types Package

### Package Information
- **Name**: `@vf-media/media-types`
- **Version**: 1.0.0
- **Description**: Shared TypeScript types and interfaces for VisualForge Media applications
- **Location**: `e:\Projects\VisualForgeMediaV2\vf-media-types\`

### Core Type Categories

#### 1. Common Base Types (`common.ts`)
```typescript
interface BaseEntity {
  id: string;
  createdAt?: Date;
  updatedAt?: Date;
}

interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}
```

#### 2. API Request/Response Types (`api.ts`)
```typescript
interface BaseGenerationRequest {
  prompt: string;
  quality?: Quality;
}

interface BaseGenerationResponse extends BaseEntity {
  status: GenerationStatus;
  progress?: number;
  error?: string;
  metadata?: Record<string, any>;
}

interface WebhookPayload<T = any> {
  eventType: 'generation.started' | 'generation.progress' | 'generation.completed' | 'generation.failed';
  timestamp: string;
  data: T;
}

interface JobRequest {
  id: string;
  type: string;
  payload: any;
  priority?: number;
  delay?: number;
  webhook?: WebhookConfig;
}
```

#### 3. Media-Specific Types (`media.ts`)
Comprehensive types for:
- **Video Generation**: `VideoGenerationRequest/Response`, `VideoEditOptions`, `VideoWizardState`
- **Image Generation**: `ImageGenerationRequest/Response`, `ImageEditOptions`, `ImageWizardState`
- **Audio Generation**: `AudioGenerationRequest/Response`, `AudioEditOptions`, `AudioWizardState`
- **Text Generation**: `TextGenerationRequest/Response`, `TextEditOptions`, `TextWizardState`

#### 4. Wizard Framework (`wizard.ts`)
```typescript
interface BaseWizardState {
  currentStep: WizardStep;
  prompt: string;
  isLoading: boolean;
  error?: string;
  progress?: number;
}

interface WizardProvider<T extends BaseWizardState = BaseWizardState> {
  state: T;
  navigation: WizardNavigation;
  actions: WizardActions;
}
```

#### 5. Enums and Constants (`enums.ts`)
- Media types, generation status, quality levels
- Aspect ratios, audio tempo/mood, text types/tones
- Size constants and polling intervals

### Usage Across Projects
The package is used in:
- `vf-utils` (SDK utilities)
- `vf-shared-components` (React components)
- `vf-bulk-generator-service` (API service)
- Multiple services in VisualForgeMediaV2

---

## Database Interface Patterns

### NiroSubs-V2 Pattern (Drizzle ORM + AWS Secrets Manager)

#### Connection Management
```typescript
interface DatabaseSecret {
  engine: string;
  host: string;
  username: string;
  password: string;
  dbname: string;
  port: number;
}

export async function getDatabase() {
  if (db) return db
  
  // Fetch credentials from AWS Secrets Manager
  const secret = await getSecret('visualforge/dev/database/main')
  const client = postgres(connectionString, {
    ssl: 'require' // AWS RDS requires SSL
  })
  
  db = drizzle(client)
  return db
}
```

#### Schema Definition Pattern
```typescript
// Consistent schema across all services
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  cognitoSub: text('cognito_sub').notNull().unique(),
  email: varchar('email', { length: 255 }).notNull(),
  name: varchar('name', { length: 255 }),
  stripeCustomerId: text('stripe_customer_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
})
```

#### Multiple Connection Strategies
1. **Secrets Manager Integration** (`database.ts`)
2. **Environment Variables** (`database-pg.ts`)
3. **Simple Connection String** (`database-simple.ts`)

### VisualForgeMediaV2 Pattern (Node-Postgres + Direct Credentials)

```typescript
// Direct PostgreSQL pool connection
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  user: 'vf_user',
  password: 'vf_password',
  database: 'visualforge',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});
```

### Database Interface Standardization

#### Common Interface Pattern
```typescript
interface DatabaseConnection {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  query<T>(sql: string, params?: any[]): Promise<T[]>;
  transaction<T>(callback: (tx: Transaction) => Promise<T>): Promise<T>;
}

interface DatabaseCredentials {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl?: boolean | object;
}
```

---

## SDK Architecture (VF-Utils)

### Package Information
- **Name**: `@vf-media/utils`
- **Version**: 1.0.0
- **Description**: Shared utility functions and formatters for VisualForge Media applications

### Core SDK Components

#### 1. API Client (`api.ts`)
```typescript
export class ApiClient {
  private axios: AxiosInstance;
  private retries: number;
  private retryDelay: number;

  constructor(config: ApiClientConfig) {
    // Automatic retry logic, request/response interceptors
    // Error formatting and timeout handling
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  // ... other HTTP methods
}

// Polling utility for long-running operations
export async function pollForCompletion<T extends BaseGenerationResponse>(
  getStatus: () => Promise<T>,
  options: { interval?: number; timeout?: number; onProgress?: (response: T) => void }
): Promise<T>
```

#### 2. Storage Utilities (`storage.ts`)
```typescript
export class Storage {
  // TTL support, serialization, prefix management
  set<T>(key: string, value: T, ttl?: number): void
  get<T>(key: string): T | null
  remove(key: string): void
  clear(): void
}

export class Cache<T> {
  async getOrSet<U extends T>(
    key: string,
    factory: () => Promise<U> | U,
    ttl?: number
  ): Promise<U>
}
```

#### 3. Advanced Polling (`polling.ts`)
```typescript
export class Poller<T> {
  // Supports exponential backoff, custom retry logic
  // Timeout handling, progress callbacks
  async poll(pollFunction: () => Promise<T>): Promise<PollingResult<T>>
}

export function pollForStatus<T extends { status: string }>(
  getStatus: () => Promise<T>,
  completedStatuses: string[] = ['completed'],
  failedStatuses: string[] = ['failed', 'error']
): Promise<PollingResult<T>>
```

#### 4. Additional Utilities
- **Formatters**: Date, number, file size formatting
- **Validation**: Input validation helpers
- **Error Handling**: Standardized error formatting
- **Constants**: Shared configuration values

---

## Secrets Management

### NiroSubs-V2 Implementation (AWS Secrets Manager)

#### Hierarchical Secret Organization
```
visualforge/
  dev/
    database/main
    stripe/keys
    cognito/config
    email/smtp
  staging/
    database/main
    stripe/keys
    cognito/config
    email/smtp
  production/
    database/main
    stripe/keys
    cognito/config
    email/smtp
```

#### Secret Interface Definitions
```typescript
interface DatabaseSecret {
  engine: string;
  host: string;
  username: string;
  password: string;
  dbname: string;
  port: number;
}

interface StripeSecrets {
  publishableKey: string;
  secretKey: string;
  webhookSecret: string;
}

interface CognitoSecrets {
  userPoolId: string;
  userPoolClientId: string;
  identityPoolId: string;
}

interface EmailSecrets {
  smtpHost: string;
  smtpPort: number;
  smtpUser: string;
  smtpPass: string;
  fromEmail: string;
}
```

#### Secret Management Client
```typescript
export class SecretsManager {
  private client: SecretsManagerClient;
  private cache: Map<string, { value: any; expiry: number }>;
  
  async getSecret<T>(secretName: string): Promise<T> {
    // Caching with TTL
    // Fallback to environment variables
    // Error handling and retry logic
  }
  
  async loadAllSecretsIntoEnv(): Promise<void> {
    // Bulk loading for Lambda cold starts
  }
}
```

#### Frontend Secret Handling
```typescript
// Custom React hook for secrets
export function useSecrets() {
  const [secrets, setSecrets] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetches public secrets only (publishable keys, etc.)
  // Never exposes sensitive secrets to frontend
}
```

### VisualForgeMediaV2 Current State
- Uses environment variables directly
- No centralized secret management
- Manual configuration per service

### Recommended Migration Pattern
```typescript
// Align with NiroSubs-V2 pattern
interface VFSecretsConfig {
  environment: 'dev' | 'staging' | 'production';
  secretPrefix: string; // 'visualforge'
  region: string;
}

// Service-specific secret interfaces
interface MediaGenerationSecrets {
  openaiApiKey: string;
  stabilityApiKey: string;
  elevenLabsApiKey: string;
}

interface DatabaseSecrets {
  connectionString: string;
  readonlyConnectionString?: string;
  migrationPassword?: string;
}
```

---

## Cross-Project Integration

### Type Sharing Strategy
```typescript
// Shared interfaces for integration
interface MediaIntegrationConfig {
  baseUrl: string;
  apiKey: string;
  webhookEndpoint: string;
  allowedOrigins: string[];
}

interface CrossProjectEvent {
  source: 'nirosubs' | 'visualforge';
  eventType: string;
  payload: any;
  timestamp: string;
  userId?: string;
}
```

### Communication Patterns

#### 1. Module Federation (Current)
- Frontend micro-frontend integration
- Runtime type checking required
- PostMessage communication

#### 2. SDK Integration (Proposed)
```typescript
// NiroSubs consuming VisualForge SDK
import { createApiClient, pollForCompletion } from '@vf-media/utils';
import { VideoGenerationRequest } from '@vf-media/media-types';

const vfClient = createApiClient({
  baseURL: 'https://api.visualforge.media',
  timeout: 30000,
  retries: 3
});
```

#### 3. Webhook Integration
```typescript
// Event-driven communication
interface WebhookHandler {
  handleMediaGeneration(event: MediaGenerationEvent): Promise<void>;
  handleUserUpdate(event: UserUpdateEvent): Promise<void>;
  handleSubscriptionChange(event: SubscriptionEvent): Promise<void>;
}
```

---

## Implementation Recommendations

### 1. Standardize Secrets Management
```typescript
// Action Items:
// 1. Migrate VisualForgeMediaV2 to AWS Secrets Manager
// 2. Implement hierarchical secret organization
// 3. Add caching and fallback mechanisms
// 4. Create shared secrets interface library

interface SecretsManagerConfig {
  region: string;
  environment: 'dev' | 'staging' | 'production';
  cacheTimeout: number;
  fallbackToEnv: boolean;
}
```

### 2. Database Interface Standardization
```typescript
// Action Items:
// 1. Create shared database interface package
// 2. Standardize connection pooling
// 3. Implement consistent schema patterns
// 4. Add migration and seeding utilities

interface DatabaseManager {
  connect(config: DatabaseConfig): Promise<DatabaseConnection>;
  migrate(direction: 'up' | 'down', steps?: number): Promise<void>;
  seed(seedData?: any): Promise<void>;
  backup(destination: string): Promise<void>;
}
```

### 3. Enhanced SDK Architecture
```typescript
// Action Items:
// 1. Extend vf-utils with more utilities
// 2. Add authentication helpers
// 3. Implement circuit breakers
// 4. Add comprehensive logging

interface SDKConfig {
  baseUrl: string;
  apiKey: string;
  timeout: number;
  retries: number;
  circuitBreaker: {
    failureThreshold: number;
    resetTimeout: number;
  };
  logging: {
    level: 'debug' | 'info' | 'warn' | 'error';
    destination: 'console' | 'file' | 'remote';
  };
}
```

### 4. Type Safety Improvements
```typescript
// Action Items:
// 1. Add runtime type validation
// 2. Implement API contract testing
// 3. Generate types from OpenAPI specs
// 4. Add integration tests

interface TypeValidationConfig {
  strict: boolean;
  allowAdditionalProperties: boolean;
  coerceTypes: boolean;
  removeAdditional: boolean;
}
```

### 5. Development Workflow Enhancements
```typescript
// Action Items:
// 1. Automated type package publishing
// 2. Version management across projects
// 3. Breaking change detection
// 4. Documentation generation

interface PackageManagementConfig {
  publishOnChange: boolean;
  semverPolicy: 'strict' | 'loose';
  changelogGeneration: boolean;
  documentationSync: boolean;
}
```

---

## Current Status Summary

### ✅ Completed
- vf-media-types package with comprehensive type definitions
- Basic SDK utilities in vf-utils package
- Extensive secrets management in NiroSubs-V2
- Multiple database connection patterns
- Module federation integration

### 🔄 In Progress
- Cross-project type sharing
- API client standardization
- Database interface alignment

### ⏳ Pending
- VisualForgeMediaV2 secrets manager migration
- Comprehensive SDK documentation
- Automated type validation
- Integration testing framework
- Performance monitoring

### 🚨 Critical Gaps
1. **Import Error**: vf-utils has incorrect import path (`@vf-media/shared-types` should be `@vf-media/media-types`)
2. **Secret Management**: VisualForgeMediaV2 lacks centralized secret management
3. **Database Patterns**: Inconsistent connection management across projects
4. **Type Validation**: Missing runtime type checking in integrations
5. **Error Handling**: Inconsistent error patterns between projects

This analysis provides the foundation for implementing robust, scalable shared libraries and standardized patterns across both projects.

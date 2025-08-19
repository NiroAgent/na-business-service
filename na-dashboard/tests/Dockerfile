FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY playwright.config.ts ./

# Install dependencies
RUN npm ci

# Install Playwright browsers
RUN npx playwright install

# Copy test files
COPY tests/ ./tests/

# Create directories for test results
RUN mkdir -p test-results playwright-report

# Set permissions
RUN chmod +x /app

# Default command
CMD ["npx", "playwright", "test"]

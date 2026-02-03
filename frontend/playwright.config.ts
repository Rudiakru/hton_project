import { defineConfig, devices } from '@playwright/test';

// On Windows, Vite often binds to IPv6 loopback (`::1`) when started with `--host localhost`.
// Using `localhost` here avoids flaky `ERR_CONNECTION_REFUSED` when `127.0.0.1` isn't bound.
const baseURL = process.env.E2E_BASE_URL || 'http://localhost:5173';
const outputDir = process.env.PLAYWRIGHT_OUTPUT_DIR || 'playwright-artifacts';

const videoMode = process.env.PW_VIDEO === '1' ? 'on' : 'retain-on-failure';

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  outputDir,
  use: {
    baseURL,
    headless: true,
    screenshot: 'only-on-failure',
    video: videoMode,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});

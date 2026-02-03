import fs from 'node:fs';
import { test } from '@playwright/test';

const enabled = process.env.CAPTURE_SCREENSHOTS === '1';
const outDir = process.env.CAPTURE_SCREENSHOTS_DIR || '../screenshots';

test.skip(!enabled, 'Set CAPTURE_SCREENSHOTS=1 to enable screenshot capture.');

test('capture 4 demo screenshots (manual run)', async ({ page }) => {
  fs.mkdirSync(outDir, { recursive: true });
  await page.goto('/');
  await page.setViewportSize({ width: 1440, height: 900 });

  await page.screenshot({ path: `${outDir}/01_landing.png`, fullPage: true });

  await page.getByTestId('start-demo').click();
  await page.getByTestId('evidence-drawer').waitFor({ state: 'visible' });
  await page.screenshot({ path: `${outDir}/02_start_demo_evidence.png`, fullPage: true });

  await page.getByTestId('next-step').click();
  await page.getByTestId('scouting-report').waitFor({ state: 'visible' });
  await page.screenshot({ path: `${outDir}/03_scouting_report.png`, fullPage: true });

  const integrityPanel = page.getByTestId('integrity-panel');
  await integrityPanel.scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${outDir}/04_verification.png`, fullPage: true });
});

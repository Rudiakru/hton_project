import { expect, test } from '@playwright/test';

test('demo path: Start Demo → Next → integrity is clean', async ({ page }) => {
  await page.goto('/');

  await page.getByTestId('start-demo').click();

  const drawer = page.getByTestId('evidence-drawer');
  await expect(drawer).toBeVisible();

  // Coach-facing header (do not show raw evidence ids to judges by default)
  const evidenceTitle = page.getByTestId('evidence-title');
  await expect(evidenceTitle).toBeVisible();
  await expect(evidenceTitle).toContainText('Game');

  // Even if someone expands details, never show raw evidence ids.
  await page.getByText('Technical details').click();
  const internalRef = page.getByTestId('evidence-id');
  await expect(internalRef).toBeVisible();
  await expect(internalRef).toContainText('Game');
  await expect(internalRef).not.toContainText('_');

  await page.getByTestId('next-step').click();

  const scouting = page.getByTestId('scouting-report');
  await expect(scouting).toBeVisible();
  await expect(scouting).toContainText('Scouting report');

  // Explicitly open first pattern evidence (even though Next may auto-open one)
  const firstPatternEvidence = page.getByTestId('pattern-evidence-0');
  if (await firstPatternEvidence.isVisible()) {
    await firstPatternEvidence.click();
    await expect(drawer).toBeVisible();
    await expect(evidenceTitle).toBeVisible();
  }

  const integrityPanel = page.getByTestId('integrity-panel');
  await integrityPanel.scrollIntoViewIfNeeded();
  await expect(integrityPanel).toBeVisible();

  const brokenRefs = page.getByTestId('broken-refs');
  await expect(brokenRefs).toHaveText('0');

  const matchCount = page.getByTestId('match-count');
  await expect(matchCount).toHaveText('6');
});

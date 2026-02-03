import { expect, test } from '@playwright/test';

/**
 * Cutline requirement: run the critical demo path 10× to surface flakes.
 * Path: Start Demo → Next → Integrity (broken_refs == 0) while evidence is open.
 */
test('demo path stability: Start Demo → Next → Integrity (10×)', async ({ page }) => {
  test.setTimeout(120_000);

  for (let i = 0; i < 10; i++) {
    await page.goto('/');

    await page.getByTestId('start-demo').click();
    const drawer = page.getByTestId('evidence-drawer');
    await expect(drawer).toBeVisible();

    // Coach-facing: do not leak raw evidence ids.
    const evidenceTitle = page.getByTestId('evidence-title');
    await expect(evidenceTitle).toBeVisible();
    await expect(evidenceTitle).toContainText('Game');

    // Even expanded details must not show raw ids.
    await page.getByText('Technical details').click();
    const internalRef = page.getByTestId('evidence-id');
    await expect(internalRef).toBeVisible();
    await expect(internalRef).toContainText('Game');
    await expect(internalRef).not.toContainText('_');

    await page.getByTestId('next-step').click();

    const scouting = page.getByTestId('scouting-report');
    await expect(scouting).toBeVisible();
    await expect(scouting).toContainText('Scouting report');

    const integrityPanel = page.getByTestId('integrity-panel');
    await expect(integrityPanel).toBeVisible();
    await expect(page.getByTestId('broken-refs')).toHaveText('0');
    await expect(page.getByTestId('match-count')).toHaveText('6');

    // Reset UI state for next loop.
    await page.getByRole('button', { name: 'Close' }).click();
  }
});

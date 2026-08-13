import { test, expect } from '@playwright/test';

test.describe('Q-Validate Enterprise Command Center UI Workflows', () => {

  test('Workflow 1: Overview Command Center Dashboard loads correctly', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/');
    await expect(page.locator('h1')).toContainText('Q-VALIDATE');
    await expect(page.getByText(/SYSTEM OVERVIEW|Q-VALIDATE/i).first()).toBeVisible();
  });

  test('Workflow 2: Device Validation Console & Fault Injection Studio', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/devices');
    await expect(page.getByText(/DEVICE/i).first()).toBeVisible();
  });

  test('Workflow 3: Device Farm Manager Matrix Visualizer', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/farm');
    await expect(page.getByText(/DEVICE FARM/i).first()).toBeVisible();
  });

  test('Workflow 4: Performance Lab & Persistence Benchmarks', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/benchmarks');
    await expect(page.getByText(/PERFORMANCE LAB|BENCHMARK/i).first()).toBeVisible();
  });

  test('Workflow 5: OpenTelemetry Trace Inspector', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/observability');
    await expect(page.getByText(/OPENTELEMETRY|TRACE/i).first()).toBeVisible();
  });

  test('Workflow 6: Live Kubernetes Command Center', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/health');
    await expect(page.getByText(/KUBERNETES|COMMAND CENTER/i).first()).toBeVisible();
  });

  test('Workflow 7: Kubernetes Resilience & Chaos Lab', async ({ page }) => {
    await page.goto('http://127.0.0.1:3000/resilience');
    await expect(page.getByText(/RESILIENCE|CHAOS|AUTOSCALER/i).first()).toBeVisible();
  });

});

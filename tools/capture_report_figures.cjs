const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const root = process.cwd();
const outDir = path.join(root, "documentation", "report_figures");
fs.mkdirSync(outDir, { recursive: true });

async function shot(page, name, url, options = {}) {
  await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
  if (options.selector) {
    await page.locator(options.selector).first().waitFor({ state: "visible", timeout: 30000 });
  }
  await page.waitForTimeout(options.wait || 2800);
  if (options.clickText) {
    await page.getByText(options.clickText, { exact: true }).click({ timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(3500);
  }
  if (options.scrollY) {
    await page.mouse.wheel(0, options.scrollY);
    await page.waitForTimeout(1800);
  }
  await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: Boolean(options.fullPage) });
  console.log(`captured ${name}`);
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1700, height: 1050 }, deviceScaleFactor: 1 });
  const base = "http://localhost:8501";
  await shot(page, "figure_4_1_home", `${base}/`, { selector: ".hero", wait: 6000 });
  await shot(page, "figure_4_2_dataset_overview", `${base}/Dataset_Overview`, { selector: ".section-title" });
  await shot(page, "figure_4_3_correlation_heatmap", `${base}/Dataset_Overview`, { scrollY: 2600 });
  await shot(page, "figure_4_4_data_visualization", `${base}/Data_Visualization`);
  await shot(page, "figure_4_5_team_comparison", `${base}/Team_Comparison`);
  await shot(page, "figure_4_6_match_prediction_form", `${base}/Match_Prediction`);
  await shot(page, "figure_4_7_prediction_output", `${base}/Match_Prediction`, { clickText: "Predict Match Outcome", scrollY: 650 });
  await shot(page, "figure_4_8_world_cup_prediction", `${base}/World_Cup_Prediction`);
  await shot(page, "figure_4_9_model_performance", `${base}/Model_Performance`);
  await shot(page, "figure_4_10_confusion_matrix", `${base}/Model_Performance`, { scrollY: 1150 });
  await shot(page, "figure_4_11_feature_importance", `${base}/Model_Performance`, { scrollY: 1850 });
  await shot(page, "figure_4_12_about_project", `${base}/About_Project`);
  await browser.close();
})();

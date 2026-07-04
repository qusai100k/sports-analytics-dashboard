const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const root = process.cwd();
const outDir = path.join(root, "presentation_screenshots");
fs.mkdirSync(outDir, { recursive: true });

const pages = [
  ["home", "http://localhost:8501/"],
  ["dataset", "http://localhost:8501/Dataset_Overview"],
  ["visualization", "http://localhost:8501/Data_Visualization"],
  ["team_comparison", "http://localhost:8501/Team_Comparison"],
  ["prediction", "http://localhost:8501/Match_Prediction"],
  ["world_cup", "http://localhost:8501/World_Cup_Prediction"],
  ["performance", "http://localhost:8501/Model_Performance"],
  ["about", "http://localhost:8501/About_Project"],
];

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  for (const [name, url] of pages) {
    await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForTimeout(3500);
    await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: false });
    console.log(`captured ${name}`);
  }
  await browser.close();
})();

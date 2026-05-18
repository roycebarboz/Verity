import { chromium } from 'playwright'

const url = process.argv[2] || 'http://localhost:5173'
const output = process.argv[3] || 'screenshot.png'
const clip = process.argv[4] ? JSON.parse(process.argv[4]) : null

const browser = await chromium.launch()
const page = await browser.newPage()
await page.setViewportSize({ width: 1440, height: 900 })
await page.goto(url, { waitUntil: 'networkidle' })
if (clip) {
  await page.screenshot({ path: output, clip })
} else {
  await page.screenshot({ path: output })
}
await browser.close()
console.log(`Screenshot saved to ${output}`)

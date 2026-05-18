import { execSync } from 'child_process'
import { existsSync } from 'fs'

// Install playwright chromium if needed, then take a screenshot
const url = process.argv[2] || 'http://localhost:5173'
const output = process.argv[3] || 'screenshot.png'

try {
  // Try playwright which supports Node 20 well
  execSync(`npx --yes playwright@1.44 screenshot --browser chromium "${url}" "${output}"`, { stdio: 'inherit' })
} catch {
  console.error('playwright failed')
}

/**
 * Offline prebuild for local forks: skip GitHub downloads when sidecars/resources
 * already exist (e.g. copied from an installed Clash Verge.app).
 */
import { execSync } from 'child_process'
import fs from 'fs'
import fsp from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const host = execSync('rustc -vV')
  .toString()
  .match(/host: (.+)/)[1]
  .trim()
const sidecarDir = path.join(root, 'src-tauri', 'sidecar')
const resourcesDir = path.join(root, 'src-tauri', 'resources')

const required = [
  path.join(sidecarDir, `verge-mihomo-${host}`),
  path.join(sidecarDir, `verge-mihomo-alpha-${host}`),
  path.join(resourcesDir, 'Country.mmdb'),
  path.join(resourcesDir, 'geoip.dat'),
  path.join(resourcesDir, 'geosite.dat'),
  path.join(resourcesDir, 'clash-verge-service'),
  path.join(resourcesDir, 'clash-verge-service-install'),
  path.join(resourcesDir, 'clash-verge-service-uninstall'),
  path.join(resourcesDir, 'set_dns.sh'),
  path.join(resourcesDir, 'unset_dns.sh'),
]

const missing = required.filter((p) => !fs.existsSync(p))
if (missing.length) {
  console.error('[prebuild-offline] missing files:')
  for (const p of missing) console.error(' -', p)
  console.error('Copy from Clash Verge.app or run: pnpm prebuild:online')
  process.exit(1)
}

for (const p of required) {
  if (!p.endsWith('.dat') && !p.endsWith('.mmdb')) {
    await fsp.chmod(p, 0o755)
  }
}

console.log('[prebuild-offline] ok — using local sidecars/resources')

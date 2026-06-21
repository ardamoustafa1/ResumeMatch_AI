import assert from "node:assert/strict"
import { readFile } from "node:fs/promises"
import test from "node:test"

const manifest = JSON.parse(
  await readFile(new URL("../extension/manifest.json", import.meta.url), "utf8"),
)
const background = await readFile(
  new URL("../extension/background.js", import.meta.url),
  "utf8",
)
const popup = await readFile(
  new URL("../extension/popup.js", import.meta.url),
  "utf8",
)
const privacy = await readFile(
  new URL("../extension/PRIVACY_POLICY.md", import.meta.url),
  "utf8",
)

test("extension uses Manifest V3 and least-privilege hosts", () => {
  assert.equal(manifest.manifest_version, 3)
  assert.deepEqual(manifest.host_permissions, [
    "https://www.linkedin.com/jobs/*",
    "http://localhost:8000/*",
  ])
  assert.deepEqual(manifest.optional_host_permissions, ["https://*/*"])
})

test("remote API hosts require HTTPS and runtime permission", () => {
  assert.match(popup, /startsWith\('https:\/\/'\)/)
  assert.match(popup, /chrome\.permissions\.request/)
})

test("analysis requests use bearer authentication", () => {
  assert.match(background, /\/api\/v1\/analysis/)
  assert.match(background, /Authorization/)
  assert.match(background, /Bearer/)
})

test("privacy policy accurately describes persistent local storage", () => {
  assert.match(privacy, /storage\.local/)
  assert.doesNotMatch(privacy, /session storage/)
})

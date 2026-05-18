# Screenshot Self-Correction Loop
**Applies to:** Session 3 (Frontend) only — do not apply during backend or infra sessions.
**Reference design:** `mock_design.html` in the repo root.

## Step 1 — Start the dev server

```
cd frontend && npm run dev
```

Backend must also be running for live API calls:
```
uvicorn verity.api:app --reload
```

## Step 2 — Take a screenshot

Use puppeteer via npx (one-time, not a permanent dependency — confirm with user before first use):

```
npx puppeteer@latest screenshot http://localhost:5173 --fullPage --output screenshot.png
```

Capture additional targeted screenshots for each major panel:
- Left panel (TicketInput)
- Center panel (PipelineTimeline with an AgentCard expanded)
- Right panel (OutcomePanel with a result loaded)
- Footer (MetricsFooter)

## Step 3 — Compare with reference

Open `mock_design.html` alongside the screenshot. Check every item below — be specific with measurements:

**Colors (exact values from mock_design.html token palette):**
- `primary`: `#000000`
- `secondary`: `#0058be`
- `secondary-container`: `#2170e4`
- `surface`: `#f7f9fb`
- `surface-container-low`: `#f2f4f6`
- `on-surface`: `#191c1e`
- `outline`: `#76777d`

**Agent card status colors (from PRD Section 7.6):**
- Pending: gray
- Running: blue
- Passed: green
- Retry: amber
- Failed: red

**Layout checklist:**
- [ ] Three-panel layout (left / center / right) with correct proportions
- [ ] Header: Verity logo + tagline + "View Repo" link
- [ ] Left panel: textarea, customer ID field, channel selector, Triage button, 4–5 preset buttons
- [ ] Center panel: five AgentCard instances (Bouncer → Librarian → Drafter → Verifier → Dispatcher)
- [ ] Drafter card shows both attempts when attempt count > 1
- [ ] Right panel: action badge, response text, citation list, verifier reasoning
- [ ] Footer: total latency, total tokens, Datadog trace ID with copy button
- [ ] Font: Inter (headings/body), JetBrains Mono (code/IDs/trace IDs)
- [ ] Tailwind only — no custom CSS files

**Spacing and sizing (be explicit):**
- "Left panel width is ~30% but reference is closer to 25%"
- "Gap between AgentCards should be 8px but is 16px"
- "Triage button border radius looks 4px instead of 8px"

## Step 4 — Fix the code

Update Tailwind classes in the relevant component. Examples:

```
gap-4 → gap-2
text-3xl → text-2xl
items-start → items-center
rounded → rounded-lg
w-1/3 → w-1/4
```

Do NOT add custom CSS. Do NOT add a dark mode toggle. Do NOT add new components beyond those listed in PRD Section 7.6.

## Step 5 — Re-screenshot and repeat

**Minimum 2 full comparison rounds required.** Do not stop after the first pass.

Continue until:
- Layout matches reference within ~2–3px
- All colors match the palette above
- All PRD Section 7.6 layout regions are present and correct
- No console errors in the browser

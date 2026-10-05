

```md
# Hirearchy — Design Notes

## Vibe

Modern editorial SaaS dashboard with a highly structured, premium interface — inspired by polished productivity, education, and healthcare dashboards, with soft pastel surfaces, bold typography, rounded containers, and strong information hierarchy.

The interface should feel **intentional, sophisticated, slightly playful, and highly usable** rather than like a generic AI-generated dashboard.

Think:
- Modern SaaS
- Editorial layout
- Structured information
- Soft pastel UI
- Strong typography
- Rounded cards
- Compact but breathable dashboards
- Minimal decorative elements

The visual language should feel closer to a **designed digital product system** than a conventional corporate dashboard.

## Colors

Primary palette inspired by the provided mauve/cherry-blossom reference.

- Primary: #4A3F4B
- Deep: #16131F
- Secondary: #806C79
- Background: #C1A0AC
- Surface: #F0D9E4
- Light Surface: #F7EEF2
- Soft Pink: #F0D9E4
- Dusty Mauve: #C1A0AC
- Plum Gray: #806C79
- Dark Plum: #4A3F4B
- Accent (success/match): #A98FA0
- Danger / attention: #8B5969
- Border: #D8C5CE

### Color philosophy

Do NOT make every element pink or purple.

The palette should work through **contrast between neutral surfaces and muted accents**.

Use:

- #16131F for strong headings and important text
- #4A3F4B for primary actions and navigation
- #806C79 for secondary information
- #F7EEF2 / #F0D9E4 for cards and surfaces
- #C1A0AC for larger background areas
- #8B5969 only for warnings or negative states
- #A98FA0 for subtle positive/match states

The UI should have plenty of near-neutral space.

## Dark or light?

Light only.

The main interface should use a warm/off-white or very pale blush canvas with dark plum navigation and typography.

A dark sidebar can be used as a major structural element, similar to the second reference.

Do not create a conventional dark mode for the primary design.

## Typography

- Sans: **Manrope**
- Display: **DM Serif Display** or **Playfair Display**
- Mono: **JetBrains Mono**

### Typography direction

Typography is one of the main visual elements.

Use:

- Large, bold headings
- Short section titles
- Compact metadata
- Strong numerical metrics
- Clear labels
- Occasional serif display typography for major editorial moments

Avoid tiny text-heavy interfaces.

Headings should have enough weight to create clear visual anchors.

## Layout

The layout should follow a **structured dashboard/editorial system** rather than a collection of floating cards.

### Overall structure

Desktop:

┌──────────────────────────────────────────────────────┐
│ Sidebar │ Header / Search / Profile                  │
│         ├──────────────────────────────┬─────────────┤
│         │                              │             │
│         │ Main Content                 │ Secondary   │
│         │                              │ Content     │
│         │                              │             │
│         ├──────────────────────────────┴─────────────┤
│         │ Supporting content / activity              │
└─────────┴────────────────────────────────────────────┘

Use a persistent left navigation rail/sidebar.

The main content area should have a strong grid.

Do not center everything.

Do not make every card the same size.

Use **large + medium + compact modules** to create hierarchy.

## Sidebar

The sidebar is an important visual anchor.

Recommended direction:

- Width: approximately 220–250px
- Dark plum/near-black surface
- Rounded outer container or softly integrated into page
- Logo at top
- User profile
- Navigation groups
- Active state highlighted with soft mauve/pink
- Minimal icons
- Small labels
- Logout/settings toward the bottom

Example structure:

Brand

MAIN
- Dashboard
- Discover
- Applications
- Deadlines

CAREER
- Resumes
- Skill Gaps
- Insights

ACCOUNT
- Profile
- Settings

The sidebar should feel compact and intentional.

## Main Content

The main dashboard should NOT look like a standard 3-column admin panel.

Use a strong editorial grid.

Example:

### Top row

Large welcome / career overview block

+

Compact profile completion / match metric

### Middle row

Large recommended opportunities section

+

Upcoming deadlines

### Bottom row

Application progress

+

Skill insights

+

Recent activity

Some sections can intentionally span 2–3 columns.

## Cards

Cards should feel like **individual modules within one larger system**.

Use:

- 16–24px radius
- Soft backgrounds
- Minimal borders
- Very subtle shadows
- Generous internal spacing
- Strong heading hierarchy

Avoid excessive floating-card effects.

Some sections can be completely borderless and rely only on background contrast.

### Card hierarchy

Primary cards:
- Larger
- Stronger background
- More visual content

Secondary cards:
- Smaller
- More compact
- Supporting information

Utility cards:
- Very compact
- Metrics, status, dates, actions

## Information Density

Aim for **medium information density**.

The UI should contain enough information to feel useful, but never become visually cramped.

Prioritize:

1. What matters now
2. What the user should do next
3. Important career metrics
4. Personalized recommendations
5. Supporting information

Avoid filling empty space just because it exists.

Whitespace is intentional.

## Dashboard

The dashboard should feel personalized.

Top area:

"Good morning, Anayya"

or

"Welcome back"

Followed by a concise summary such as:

"You're currently matching with 18 opportunities."

Possible dashboard modules:

- Profile completion
- Career match score
- Recommended opportunities
- Applications in progress
- Upcoming deadlines
- Resume health
- Skill gaps
- Recent activity

### Hero / Welcome section

Use a large editorial-style welcome section.

Include:

- Greeting
- Short personalized message
- Main career metric
- Primary CTA

Example:

"Good morning 👋"

"3 new opportunities match your profile."

[Explore opportunities]

## Discover Page

Discover should feel like a **premium opportunity discovery platform**, not a job-board clone.

Top:

- Page title
- Search
- Filters
- Match summary

Opportunity cards should include:

- Company
- Position
- Location
- Job type
- Match %
- Required skills
- Deadline
- Save/bookmark
- Apply CTA

Use large visual cards for featured opportunities.

Use compact rows/cards for the remaining listings.

## Applications

Use a visual application management system.

Possible statuses:

- Saved
- Applied
- Screening
- Interview
- Offer
- Rejected

Applications can be presented as:

- Kanban-style columns
- Timeline
- Compact cards

Do not make it look like a spreadsheet.

Each application should show:

- Company
- Role
- Status
- Date applied
- Next action
- Match score

## Deadlines

Focus strongly on dates.

Use:

- Calendar
- Upcoming deadline cards
- Timeline
- Priority indicators

Important deadlines should be visually obvious.

Use muted pink/mauve accents rather than bright red.

## Resumes

Treat resumes as **documents within a workspace**.

Use:

- Resume preview cards
- Completion score
- Last updated
- Version name
- ATS/readiness score
- Improvement suggestions

Primary CTA:

"Improve Resume"

Secondary:

"View Resume"

## Skill Gaps

Make this page highly visual.

Possible layout:

Current Skills

        ↓

Required Skills

        ↓

Skill Gaps

Use:

- Progress bars
- Skill chips
- Match percentages
- Small comparison charts
- Recommended learning cards

Avoid huge complicated graphs.

## Insights

Insights should feel like **personalized recommendations**, not business analytics.

Examples:

"You are strongest in frontend development."

"Your profile matches 72% of entry-level UI roles."

"Adding Figma to your skills could improve your match score."

Each insight can be represented as a compact visual card.

## Profile

Use a strong profile header.

Include:

- Avatar
- Name
- Role
- Education
- Location
- Profile completion

Then divide information into:

- About
- Skills
- Education
- Experience
- Projects
- Certifications

Use cards sparingly.

Timeline layouts are preferred for experience and education.

## Settings

Simple, structured settings interface.

Sections:

- Account
- Profile
- Preferences
- Notifications
- Privacy
- Appearance

Use:

- Toggles
- Segmented controls
- Select inputs
- Clean form fields

Avoid dense admin-style tables.

## Buttons

Primary:

- Background: #4A3F4B
- Text: #F7EEF2

Secondary:

- Background: #F0D9E4
- Text: #4A3F4B

Ghost:

- Transparent
- Text: #806C79

Buttons should have medium rounded corners.

Avoid extremely pill-shaped buttons everywhere.

Use pills primarily for:

- Tags
- Statuses
- Match percentages
- Filters

## Search

Search should be visually prominent but compact.

Use:

- Rounded rectangular input
- Search icon
- Soft background
- Minimal border

Example:

[ 🔍  Search opportunities, skills, companies... ]

Search can sit in the global header.

## Status / Tags

Use compact rounded tags.

Examples:

`MATCH 92%`

`REMOTE`

`FULL-TIME`

`APPLIED`

`INTERVIEW`

`HIGH PRIORITY`

Tags should use muted versions of the palette.

Avoid rainbow-colored tags.

## Metrics

Metrics should be visually strong.

Example:

72%

Career Match

18

Applications

04

Interviews

06

Skills to improve

Use large numbers and small supporting labels.

Do not overuse charts when a number communicates the information better.

## Charts

Charts should be minimal and editorial.

Use:

- Thin line charts
- Simple progress bars
- Circular progress
- Small comparison charts

Avoid:

- 3D charts
- Dense dashboards
- Multiple colors
- Heavy gridlines
- Corporate BI aesthetics

Charts should use the mauve palette.

## Icons

Use **Lucide Icons**.

Style:

- Thin/medium stroke
- 16–20px
- Consistent sizing
- Minimal visual noise

Icons should support the UI rather than become decorative elements.

## Borders

Borders should be subtle.

Preferred:

`#D8C5CE`

Avoid strong black borders around every component.

Use borders primarily for:

- Inputs
- Tables
- Separators
- Interactive states

Most cards should rely on surface contrast instead.

## Shadows

Very subtle.

Preferred direction:

`0 6px 24px rgba(74, 63, 75, 0.06)`

Never use heavy black drop shadows.

Depth should primarily come from:

1. Surface color
2. Spacing
3. Border
4. Very subtle shadow

## Radius

Use a consistent radius system.

- Small: 8px
- Medium: 12px
- Card: 18px
- Large container: 24px
- Pills: 999px

Do not make every element extremely rounded.

The overall product should feel refined rather than overly "cute".

## Animations

Subtle and polished.

Use:

- 150–250ms hover transitions
- Soft card elevation
- Fade/slide page transitions
- Progress animation
- Button press feedback
- Smooth sidebar interactions

Avoid:

- Excessive bouncing
- Large spring animations
- Constant motion
- Decorative animations

Animation should make the product feel responsive, not distracting.

## Responsive Behavior

### Desktop

Full sidebar + multi-column dashboard.

### Tablet

Collapsed sidebar + 2-column content.

### Mobile

- Sidebar becomes drawer
- Single-column content
- Horizontal scrolling where necessary
- Large cards become stacked modules
- Metrics become 2-column grids

Never shrink desktop layouts excessively to fit mobile.

## Visual Composition

The design should use **large blocks of visual hierarchy**.

Think:

Large heading

↓

Large primary module

↓

Supporting modules

↓

Compact information

Instead of:

Heading

↓
10 identical cards

↓
10 more identical cards

The page should have an obvious visual rhythm.

## Reference sites

- https://linear.app/
- https://www.notion.so/
- https://www.stripe.com/
- https://www.airbnb.com/

Use these for UX and product-system inspiration only.

The visual identity must remain specific to Hirearchy.

## Pages to design (from spec)

- Dashboard
- Discover
- Applications
- Deadlines
- Resumes
- Skill Gaps
- Insights
- Profile
- Settings

## Component library

Tailwind CSS + shadcn/ui is the default recommendation.

Use:

- Tailwind CSS
- shadcn/ui
- Radix UI
- Lucide Icons
- Recharts

Create custom Hirearchy components on top of shadcn rather than using default shadcn styling unchanged.

Important custom components:

- Hirearchy Sidebar
- Opportunity Card
- Match Score
- Application Card
- Deadline Card
- Skill Card
- Resume Card
- Insight Card
- Career Metric
- Profile Completion
- Status Badge
- Search Bar
- Filter Bar
- Activity Timeline
- Progress Indicator

## Design System Rule

The interface should look like **one carefully designed product**, not a collection of UI-kit components.

Every page should share:

- Same typography
- Same spacing system
- Same border radius
- Same color palette
- Same iconography
- Same interaction language

But individual pages should have different compositions depending on their purpose.

## What to Avoid

Do NOT use:

- Generic SaaS blue/purple gradients
- Excessive glassmorphism
- Huge rounded pills everywhere
- Identical cards repeated across the page
- Excessive shadows
- Neon colors
- Rainbow dashboards
- Dense enterprise tables
- Excessive charts
- Generic AI-dashboard aesthetics
- Excessive empty space with no useful hierarchy
- Overly cute/pastel "student app" styling

The pastel palette should feel **mature and premium**, not childish.

## Overall Design Principle

**Structured like a professional SaaS product. Styled like a premium editorial interface.**

The first reference establishes the idea of:

- Soft rounded modules
- Friendly dashboard
- Pastel accents
- Strong visual hierarchy
- Large content areas

The second set of references establishes:

- Strong information architecture
- Dark sidebar
- Dense but readable information
- Editorial typography
- Structured grids
- Professional product feel
- Clear separation between navigation and content

The Hirearchy interface should combine these qualities while maintaining its own identity.

The final result should feel like:

**"A premium career intelligence platform"**

rather than:

**"A pastel student dashboard."**
```
## Animation & Motion

### Level
Level 2 — Expressive.

### Library
- `motion` (framer-motion successor) for page transitions, springs, layout animations
- `@formkit/auto-animate` for lists
- `react-countup` for animated metrics
- Tailwind utilities for trivial hover/focus states

### Principles
- Motion explains state changes, never decorates
- Interactive feedback: ≤200ms
- Transitions and reveals: 300–800ms
- Spring physics default: `{ type: "spring", stiffness: 260, damping: 26 }`
- Respect `prefers-reduced-motion` (wrap all `motion` usage)

### Where we animate
[list the moments above]

### Where we don't
- No wiggles on hover
- No bounce on click
- No sound
- No confetti except at OFFER
- No infinite looping animations except subtle overdue pulse
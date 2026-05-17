# Web Engineering Crew
**Date:** 2026-04-26
## Project Overview
Built an AI-powered crew (`web_engineering_crew`) that autonomously designs, builds, and reviews premium landing pages using a multi-agent pipeline. The crew generates HTML/CSS/JS with Apple/Stripe-level motion graphics, custom cursors, 3D tilt effects, and premium animations.

## Key Details
- **Framework:** CrewAI 1.12.2 with imperative pattern (not @CrewBase decorator)
- **Models Used:**
  - `deepseek/deepseek-reasoner` → Designer (UI/UX Director) and Reviewer (QA)
  - `deepseek/deepseek-v4-flash` → Frontend (HTML/Tailwind builder)
  - `deepseek/deepseek-v4-pro` → Motion (Creative Interaction Engineer)
  - `deepseek-chat` → Requirements analysis phase (direct API call)
- **Pipeline Phases:**
  1. **Phase 0:** Direct DeepSeek API → RequirementsAnalysis (JSON structured output)
  2. **Phase 1:** Dynamic crew construction from YAML config + analysis conditions
  3. **Phase 2:** Sequential crew execution: Design → HTML → CSS → Review
  4. **Phase 3:** Post-hoc JSON parsing of raw task output → Pydantic validation
- **Architecture:**
  - YAML-driven agent/task config (`agents.yaml`, `tasks.yaml`)
  - Dynamic task filtering via `condition` fields (`needs_motion`, `needs_review`)
  - JSON schemas embedded in task descriptions (DeepSeek doesn't support OpenAI structured output)
  - `_try_parse_json()` handles markdown fences and malformed JSON with regex fallback
- **Output Models:** `RequirementsAnalysis`, `DesignDoc`, `HtmlModule`, `CssModule`, `ReviewReport`, `PipelineOutput`

## Pipeline Run Results
- **Design Doc:** Generated successfully with color scheme, typography, layout, components, motion plan
- **HTML:** Generated full premium page (56KB) but output was raw HTML wrapped in markdown fences (not JSON `{"source_code": "..."}` format) → saved as `task_1_raw.txt`
- **CSS:** Generated successfully (14KB) with all 10 specified animations (cursor, tilt, word reveal, stagger, scroll, page transition, magnetic buttons, section line, stat shimmer, mobile menu)
- **Review:** Score 7/10, NOT approved. Issues identified: word reveal breaking HTML structure, cursor accessibility, missing mobile hamburger, no `<main>` landmark, carousel auto-advance without pause

## Enhancements Applied to Existing Website
The generated pipeline output was applied to improve the existing Mystery Shopper Website at `/Mystery Shopper Website/`:

1. **CSS (styles.css):** Added grain texture, page transition overlay, word-by-word reveal, shimmer effect, section divider gradients, testimonial carousel, tilt-card glare, enhanced cursor and magnetic button transitions, prefers-reduced-motion accessibility
2. **JS (script.js):** Added word-by-word hero reveal, testimonials carousel with auto-rotate/dots, internal link page transitions
3. **HTML (index.html):** Added page transition overlay, grain texture overlay, hero headline ID for word reveal, section dividers, testimonials section, shimmer stat numbers, 25+ years badge with pulse animation

## Progress Log
- 2026-04-26: Created project files (pyproject.toml, models, config, crew, main)
- 2026-04-26: Fixed import errors (missing RequirementsAnalysis model), updated model names to V4 variants
- 2026-04-26: First pipeline run completed successfully (4 agents, 4 tasks)
- 2026-04-26: Applied generated output to enhance existing Mystery Shopper Website

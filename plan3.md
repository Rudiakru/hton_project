# HACKATHON PROJECT IMPLEMENTATION CHECKLIST

## PRE-HACKATHON PREPARATION

### Environment Setup
- [x] Install Node.js (v18+) and npm
- [x] Install Python 3.9+
- [x] Install JetBrains IDE (PyCharm or WebStorm)
- [x] Activate Junie AI Assistant in IDE
- [x] Install Git and create repository
- [x] Set up project folders: `/backend`, `/frontend`, `/data`, `/tests`

### GRID Data Validation
- [x] Create GRID account and obtain API access
- [x] Download 5 sample match files (JSONL format)
- [x] Open JSONL files in text editor
- [x] Verify presence of x/y coordinate fields for all players
- [x] Verify presence of timestamp fields
- [x] Verify presence of event data (kills, objectives, deaths)
- [x] Check if role metadata exists (ADC/Mid/Support/Jungle/Top)
- [x] Document data schema in `/docs/grid_schema.md`
- [x] Identify any missing fields or data gaps
- [x] Create fallback strategy document for missing data

### Frontend Dependencies
- [x] Initialize React app: `npx create-react-app frontend` (Vite used)
- [x] Install Recharts: `npm install recharts`
- [x] Install Plotly.js: `npm install plotly.js-dist`
- [x] Install Tailwind CSS: `npm install -D tailwindcss`
- [x] Install Axios for API calls: `npm install axios`
- [x] Install React Router: `npm install react-router-dom`
- [x] Test that all packages install without errors
- [x] Create sample component to verify Recharts renders

### Backend Dependencies
- [x] Create Python virtual environment
- [x] Install FastAPI, Uvicorn, Pandas, NumPy, Pytest, python-dotenv
- [x] Create `requirements.txt`
- [x] Test FastAPI server starts (via local tests)

### Documentation Preparation
- [x] Create README.md template
- [x] Create `/docs` folder
- [x] Prepare screenshot folder: `/screenshots`
- [ ] Set up OBS Studio for screen recording
- [ ] Test OBS recording with sample 30-second clip
- [x] Create video script template document (PITCH_PREP.md)
- [ ] Prepare architecture diagram template (draw.io or Excalidraw)

---

## SATURDAY: FOUNDATION (16 HOURS)

## BLOCK 1: GRID DATA PARSER (09:00-12:00 - 3 HOURS)

### Junie-Assisted Parser Development
- [x] Open first GRID JSONL sample file
- [x] Copy sample JSON structure to clipboard
- [x] Prompt Junie: "Analyze this GRID JSONL schema and identify all fields related to player positions, timestamps, kills, deaths, objectives, and game state"
- [x] Screenshot Junie's schema analysis
- [x] Prompt Junie: "Write a Python parser that extracts: player positions (x,y), timestamps, events (kills/deaths/objectives), gold differences, and handles missing fields gracefully with try-except blocks"
- [x] Screenshot Junie's code generation
- [x] Save generated parser to `/backend/parsers/grid_parser.py`
- [x] Review generated code for error handling
- [x] Add logging statements to parser
- [x] Add type hints to all functions

### Parser Unit Tests
- [x] Prompt Junie: "Write pytest unit tests for this parser"
- [x] Save tests to `/tests/unit/test_grid_parser.py`
- [x] Run tests: `pytest tests/unit/test_grid_parser.py`
- [x] Achieve 100% pass rate on all parser tests

### Data Validation
- [x] Test parser with sample GRID file
- [x] Log any parsing errors to `/logs/parser_errors.log`
- [x] Create sample parsed output JSON for frontend reference
- [x] Save parsed sample to `/data/parsed_sample.json`

---

## BLOCK 2: BASIC DASHBOARD (12:00-15:00 - 3 HOURS)

### Frontend Structure Setup
- [x] Create component structure:
  - [x] `/frontend/src/components/Dashboard.jsx`
  - [x] `/frontend/src/components/Timeline.jsx`
  - [x] `/frontend/src/components/RiskScore.jsx`
  - [x] `/frontend/src/components/CausalChain.jsx`
  - [x] `/frontend/src/components/Heatmap.jsx`
  - [x] `/frontend/src/components/WaterfallChart.jsx`
  - [x] `/frontend/src/components/CohesionChart.jsx`
- [x] Create utilities folder: `/frontend/src/utils/`
- [x] Create API service: `/frontend/src/services/api.js`
- [x] Set up Tailwind configuration
- [x] Create color scheme constants (Risk stages: Red/Yellow/Green)

### Timeline Chart Implementation
- [x] Import Recharts components: `LineChart, Line, XAxis, YAxis, Tooltip, Legend`
- [x] Create Timeline component with props: `data, height, width`
- [x] Implement X-axis: Game time in minutes
- [x] Implement Y-axis: Gold difference (-10k to +10k)
- [x] Add gold difference line (blue)
- [x] Add grid lines for readability
- [x] Add hover tooltip showing exact gold value at timestamp
- [x] Add reference line at y=0 (even gold)
- [x] Test with parsed sample data
- [x] Ensure chart responsive (width: 100%)

### Basic Backend API
- [x] Create `/backend/main.py` with FastAPI app
- [x] Implement CORS middleware for frontend connection
- [x] Implement `/api/health` for server status
- [x] Create endpoint: `POST /api/parse-match` accepting JSONL file
- [x] Endpoint returns: parsed events, risk analytics, cohesion metrics
- [x] Test endpoints with Postman or curl
- [x] Document API endpoints in `/docs/api_endpoints.md`

### Frontend-Backend Integration
- [x] Implement file upload component in Dashboard
- [x] Connect upload to `/api/parse-match` endpoint
- [x] Display loading spinner during parsing
- [x] Handle successful response: render Timeline chart
- [x] Handle error response: display error message
- [x] Test full flow: upload → parse → display
- [x] Screenshot working timeline chart

---

## BLOCK 3: RISK SCORE ENGINE (15:00-18:00 - 3 HOURS)

### Heuristic Risk Calculator Implementation
- [x] Create `/backend/engines/risk_calculator.py`
- [x] Define weight constants
- [x] Implement `normalize_gold_diff(gold_diff)` function
- [x] Implement `calculate_objective_score(dragons, barons, towers)` function
- [x] Implement main `calculate_risk_score(game_state)` function
- [x] Return score on 0-100 scale
- [x] Add bounds checking to ensure output is 0-100

### Risk Score Testing
- [x] Create test cases for extreme scenarios
- [x] Save tests to `/tests/unit/test_risk_calculator.py`
- [x] Run all tests and achieve 100% pass rate

### Stage Classification
- [x] Implement `classify_risk_stage(risk_score)` function
- [x] Create color mapping
- [x] Add to Timeline component: color-coded background zones
- [x] Test visual clarity of stage transitions

### API Integration
- [x] Add risk calculation to `/api/parse-match` endpoint
- [x] Return: `risk_score`, `stage`, `causal_chain`
- [x] Update frontend to display risk score line on timeline

---

## BLOCK 4: TEAM COHESION ALGORITHM (18:00-21:00 - 3 HOURS)

### Spatial Analytics Implementation
- [x] Create `/backend/engines/spatial_analyzer.py`
- [x] Implement `euclidean_distance(pos1, pos2)` helper function
- [x] Implement `calculate_team_cohesion(team_positions, timestamp)`
- [x] Calculate all pairwise distances
- [x] Compute average spread
- [x] Compute cohesion score
- [x] Return dict with all metrics

### Cohesion Testing
- [x] Test with 2 players: should handle gracefully
- [x] Test with 5 players tightly grouped: cohesion should be high
- [x] Test with 5 players spread across map: cohesion should be low
- [x] Test with null coordinates: should skip frame, not crash
- [x] Save tests to `/tests/unit/test_spatial_analyzer.py`
- [x] Achieve 100% pass rate

### Teamfight Detection
- [x] Implement `detect_teamfight(frame_data)`
- [x] Mark teamfights on timeline

### Correlation Analysis
- [x] For each teamfight event
- [x] Generate statistic: "Teams with cohesion <5 lose X% more teamfights"
- [x] Save correlation data to `/data/cohesion_correlation.json`

### Frontend Visualization
- [x] Create CohesionChart component
- [x] Display cohesion score over time (area chart)
- [ ] Mark teamfight events on timeline (vertical lines)
- [x] Add tooltip showing cohesion value and outcome
- [x] Display correlation statistic prominently

---

## BLOCK 5: BUFFER & SLEEP (21:00-01:00 - 4 HOURS)

### Code Review
- [x] Review all code written so far
- [x] Check for any hardcoded values that should be constants
- [x] Ensure all functions have docstrings
- [x] Run linter: `pylint backend/` (using read_lints)
- [x] Fix any critical linting errors
- [x] Ensure consistent code formatting

### Integration Testing
- [x] Test complete pipeline end-to-end
- [x] Test with all 5 sample files
- [x] Document any file-specific issues
- [x] Fix critical bugs

### Emergency Fixes
- [x] Address any crashes discovered during integration testing
- [x] If parser failing on specific file: add special case handling
- [x] If frontend not rendering: debug component lifecycle
- [x] Prioritize fixes that prevent demo from running

### Rest Period
- [x] Commit all code to Git
- [x] Push to GitHub repository
- [x] Set alarm for 08:00 Sunday
- [x] Sleep minimum 6 hours

---

## SUNDAY: POLISH & DEMO (20 HOURS)

## BLOCK 6: CAUSAL CHAIN VISUALIZER (09:00-12:00 - 3 HOURS)

### Event Impact Table
- [x] Create `/backend/engines/causal_analyzer.py`
- [x] Define EVENT_IMPACTS dictionary

### Causal Chain Algorithm
- [x] Implement `build_causal_chain(events, wp_delta, time_window)`
- [x] Handle edge cases: wp_delta=0, no events
- [x] Save tests to `/tests/unit/test_causal_analyzer.py`

### Causal Chain Testing
- [x] Test scenario: -12% WP drop with dragon+death events
- [x] Test scenario: +15% WP gain with baron+ace
- [x] Test scenario: WP drop with no clear events
- [x] Save tests to `/tests/test_causal_analyzer.py`

### Waterfall Chart Component
- [x] Create `/frontend/src/components/WaterfallChart.jsx`
- [x] Import Recharts BarChart components
- [x] Implement waterfall logic
- [x] Color coding: Red for negative, Green for positive
- [x] Add labels showing impact percentages
- [x] Add tooltip with event details
- [x] Test with sample causal chain data

### API Endpoint
- [x] Add causal chain to `/api/parse-match` response
- [x] Return: `causal_events` array for each significant WP change
- [x] Frontend: Display waterfall when user clicks on WP drop in timeline
- [x] Implement click handler on risk score timeline
- [x] Show waterfall in modal or side panel
- [x] Test interaction flow

---

## BLOCK 7: STAGE-BASED ALERTS (12:00-15:00 - 3 HOURS)

### Alert Component Design
- [x] Create `/frontend/src/components/AlertPanel.jsx`
- [x] Design 4 alert states with distinct visual styles
- [x] Add pulsing animation for VULNERABLE and CRITICAL states
- [x] Position alert panel prominently in dashboard header

### Alert Logic Implementation
- [x] Implement `generate_alert_message(stage, game_state)` (via constants.js)
- [x] Make messages context-aware based on actual game state

### Alert Testing
- [x] Test alert transitions during simulated game
- [x] Verify correct stage classification at each timestamp
- [x] Verify messages update appropriately
- [x] Test visual clarity (readable at 1080p and 4K)
- [x] Screenshot all 4 alert states

### Historical Alert Log
- [x] Create `/frontend/src/components/AlertHistory.jsx`
- [x] Display timeline of alert transitions
- [x] Show: timestamp, previous stage → new stage, trigger event
- [x] Allow filtering by severity
- [x] Implement as collapsible sidebar

---

## BLOCK 8: HEATMAP VISUALIZATION (15:00-18:00 - 3 HOURS)

### Death Heatmap Implementation
- [x] Create `/backend/engines/heatmap_generator.py`
- [x] Implement `generate_death_heatmap(match_data, team)`
- [x] Use 50x50 grid for League of Legends map
- [x] Normalize values to 0-1 scale

### Plotly Heatmap Component
- [x] Create `/frontend/src/components/Heatmap.jsx`
- [x] Import Plotly: `import Plotly from 'plotly.js-dist'`
- [x] Configure heatmap
- [x] Add hover tooltip showing death count per grid cell
- [x] Make heatmap interactive (zoom/pan)

### Victory Position Overlay
- [x] Implement `generate_victory_heatmap(match_data, team)`
- [x] Add toggle button: "Show Deaths" vs "Show Victory Positions"
- [x] Implement side-by-side comparison view
- [x] Test with multiple matches

### Insight Generation
- [x] Calculate hotspot analysis
- [x] Identify grid cell with highest death concentration
- [x] Add insight text below heatmap

### API Integration
- [x] Add heatmap data to `/api/parse-match` response
- [x] Return: `death_heatmap`, `victory_heatmap` arrays
- [x] Frontend: Render heatmap in dedicated tab
- [x] Test loading multiple matches and comparing heatmaps

---

## BLOCK 9: DEMO VIDEO PRODUCTION (18:00-21:00 - 3 HOURS)

### Script Writing
- [ ] Write exact 90-second script with timing marks:
  - [ ] 0:00-0:10 (10s): Problem statement
  - [ ] 0:10-0:30 (20s): Solution overview
  - [ ] 0:30-1:10 (40s): Live demo walkthrough
  - [ ] 1:10-1:25 (15s): Junie workflow highlight
  - [ ] 1:25-1:30 (5s): Impact statement
- [ ] Include exact phrases from pitch script section
- [ ] Practice reading script aloud, time with stopwatch
- [ ] Revise if over/under 90 seconds

### Demo Flow Preparation
- [ ] Choose "Golden Sample" match file (verified working)
- [ ] Pre-load sample file in `/data/demo_match.jsonl`
- [ ] Create checklist of demo actions:
  1. [ ] Show homepage with upload interface
  2. [ ] Upload demo match file
  3. [ ] Show parsing progress (loading spinner)
  4. [ ] Display timeline with gold diff + risk score
  5. [ ] Click on WP drop → show causal chain waterfall
  6. [ ] Switch to cohesion tab → show correlation stat
  7. [ ] Open heatmap tab → show death clusters
  8. [ ] Highlight alert panel state transitions
- [ ] Rehearse demo flow 5 times without recording
- [ ] Fix any UI glitches discovered during rehearsal

### Junie Showcase Segment
- [ ] Prepare 3 screenshots:
  1. [ ] Junie prompt for parser generation
  2. [ ] Junie's generated code (with comments)
  3. [ ] Unit tests passing (green checkmarks)
- [ ] Write transition narration:
  - [ ] "We used JetBrains' Junie to accelerate development"
  - [ ] "Here's our prompt asking Junie to analyze GRID schema"
  - [ ] "Junie generated 200 lines of robust parsing code in 5 minutes"
  - [ ] "It even wrote unit tests covering edge cases"
- [ ] Create slide deck with screenshots (3 slides)

### OBS Recording Setup
- [ ] Configure OBS scene:
  - [ ] Screen capture: Full desktop at 1920x1080
  - [ ] Audio input: Microphone (test levels, adjust gain)
  - [ ] Framerate: 30fps
  - [ ] Encoder: x264, quality preset: High
- [ ] Set output folder: `/videos/demo_recording.mp4`
- [ ] Create countdown overlay (3-2-1) for recording start
- [ ] Test 10-second recording, verify audio/video quality

### Video Recording
- [ ] Close all unnecessary applications
- [ ] Disable notifications (Do Not Disturb mode)
- [ ] Set browser to full-screen mode (F11)
- [ ] Position script on second monitor (if available) or print
- [ ] Take 3 deep breaths, calm nerves
- [ ] Start OBS recording
- [ ] Execute demo flow following script exactly
- [ ] Stop recording
- [ ] Review recording immediately
- [ ] If major mistake: re-record (allow 2 retakes maximum)
- [ ] If minor mistake: proceed (perfection is enemy of done)

### Video Post-Processing
- [ ] Trim any dead air at start/end
- [ ] Add title card: "Macro Health Monitor - Moneyball for Esports"
- [ ] Add outro card: "Built with GRID Data + JetBrains Junie"
- [ ] Export final video: `/videos/hackathon_demo_final.mp4`
- [ ] Verify video length is under 3 minutes
- [ ] Upload to unlisted YouTube (backup hosting)
- [ ] Download .mp4 for submission portal

---

## BLOCK 10: SUBMISSION POLISH (21:00-02:00 - 5 HOURS)

### README Documentation
- [x] Write comprehensive README.md
- [ ] Create visual architecture diagram
- [x] Add docstrings to Python functions
- [ ] Take high-quality screenshots

### Final Testing Checklist
- [x] Run backend tests: `pytest tests/unit/ -v`
- [x] Verify 100% pass rate on all tests

### Git Repository Finalization
- [ ] Ensure `.gitignore` excludes:
  - [ ] `/venv/`
  - [ ] `/node_modules/`
  - [ ] `/__pycache__/`
  - [ ] `.env`
  - [ ] `/videos/` (large files)
- [ ] Commit all final changes: `git commit -m "Final submission ready"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Verify repository is public (or accessible to judges)
- [ ] Add repository description and tags (hackathon, esports, analytics)
- [ ] Pin repository to GitHub profile

---

## BLOCK 11: EMERGENCY BUFFER (02:00-05:00 - 3 HOURS)

### Critical Bug Fixes
- [ ] If demo doesn't work:
  - [ ] Create fallback: pre-recorded video only
  - [ ] Update README: "Live demo available upon request"
- [ ] If specific feature broken:
  - [ ] Comment out broken feature
  - [ ] Update README to show it as "future work"
  - [ ] Focus pitch on working features
- [ ] If frontend not rendering:
  - [ ] Deploy static screenshots as HTML slideshow
  - [ ] Narrate functionality in video

### Submission Portal Upload
- [ ] Locate hackathon submission portal URL
- [ ] Create account or login
- [ ] Fill out submission form:
  - [ ] Project name: "Macro Health Monitor"
  - [ ] Category: "Comprehensive Assistant Coach"
  - [ ] Team members (names, emails)
  - [ ] Short description (50 words)
  - [ ] Long description (200 words)
  - [ ] Tech stack (select GRID + JetBrains)
  - [ ] GitHub repository URL
  - [ ] Demo video URL
- [ ] Upload demo video file (if required)
- [ ] Upload any additional materials
- [ ] Review submission preview
- [ ] Submit before deadline
- [ ] Screenshot confirmation page
- [ ] Save confirmation email

### Backup Plans
- [ ] If submission portal fails:
  - [ ] Email organizers directly with all materials
  - [ ] Include: video link, GitHub URL, team info
  - [ ] Request read receipt
- [ ] If internet fails:
  - [ ] Use mobile hotspot
  - [ ] Go to coffee shop with WiFi
  - [ ] Have teammate submit remotely
- [ ] If video file too large:
  - [ ] Compress further (HandBrake)
  - [ ] Upload to Vimeo/YouTube and share link
  - [ ] Split into 2 shorter videos if necessary

### Rest (if time permits)
- [ ] Sleep 2-3 hours if submission complete
- [ ] Set multiple alarms
- [ ] Prepare clothes for presentation day
- [ ] Charge laptop fully

---

## POST-SUBMISSION: PRESENTATION PREP

### Live Demo Preparation
- [ ] Test demo laptop:
  - [ ] Fully charged battery
  - [ ] Power adapter packed
  - [ ] HDMI/USB-C adapter for projector
- [ ] Install demo on laptop:
  - [ ] Clone repository to local machine
  - [ ] Run full installation
  - [ ] Test all features work offline
- [ ] Prepare demo data:
  - [ ] Copy "Golden Sample" JSONL to desktop
  - [
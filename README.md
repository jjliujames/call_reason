# Call Center Insights Dashboard

A comprehensive executive dashboard for call center analytics, featuring:
- Interaction-level detail view with 3-column layout
- Taxonomy drill-down (Line of Business → Call Reason → Product)
- Complaint analysis with AI-powered root cause detection
- Agent performance tracking and coaching identification
- Actionable recommendations with impact scoring

## Tech Stack

- **Frontend**: Vue 3 (Composition API) + Vite + Pinia + Vue Router + ApexCharts
- **Backend**: Python FastAPI with in-memory fake data generation
- **Styling**: TD-like green theme with clean enterprise look

## Project Structure

```
/backend
├── main.py               # FastAPI application and endpoints
├── data_generator.py     # Fake data generation (90 days, ~11k interactions)
├── root_cause_engine.py  # Deterministic LLM simulation for root cause analysis
├── taxonomy.py           # Taxonomy definitions (LOB, Call Reason, Product)
└── requirements.txt      # Python dependencies

/frontend
├── src/
│   ├── main.js           # Vue app entry point
│   ├── App.vue           # Root component with sidebar
│   ├── router/           # Vue Router configuration
│   ├── stores/           # Pinia store (globalFilters, navigationContext)
│   ├── services/         # Axios API client
│   ├── components/       # Reusable components
│   │   ├── SidebarNav.vue
│   │   ├── BreadcrumbBar.vue
│   │   ├── GlobalFilterBar.vue
│   │   ├── InteractionTable.vue
│   │   └── RootCauseCards.vue
│   ├── views/            # Page components
│   │   ├── InteractionsList.vue
│   │   ├── InteractionDetail.vue
│   │   ├── CallReasonView.vue
│   │   ├── ComplaintsView.vue
│   │   ├── AgentsView.vue
│   │   ├── RootCauseView.vue
│   │   └── ActionsView.vue
│   └── assets/           # CSS styles
├── package.json
├── vite.config.js        # Vite config with API proxy
└── index.html
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

## Features

### Phase 1: Interaction Detail (Core)

**Route: /interactions/:id**

Three-column layout showing:
- **Left**: Interaction summary, taxonomy path, complaint info
- **Center**: Customer issue/notes, AI summary, detected root cause, recommended actions
- **Right**: Operational metrics (handle time, transfers, FCR), digital opportunity, revenue impact

**Bottom Section**: Related interactions with tabs for:
- Same Call Reason & Product
- Same Agent
- Same Complaint Category

Includes "Run Root Cause Analysis on Related" button.

### Phase 2: Rollup Views

**Call Reason View** (/call-reasons)
- KPI cards, volume trends, complaint trends
- Drill-down table by LOB → Call Reason → Product
- Bar chart visualization

**Complaints View** (/complaints)
- Complaint KPIs, category donut chart, severity distribution
- Category breakdown table
- Recent complaints with root cause analysis button

**Agents View** (/agents)
- Top performers and needs improvement lists
- Region performance chart
- Full agent table with metrics

### Phase 3: Insights

**Root Cause Analysis** (/root-cause)
- Run analysis with current filters
- Systemic vs Agent-Concentrated classification
- Impact score distribution chart

**Actions & Opportunities** (/actions)
- Prioritized action list from root cause analysis
- Filter by action type (Policy/Process/Digital/Training)
- Digital deflection opportunities
- Agent training priorities

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/options` | GET | Taxonomy lists, regions, agents |
| `/api/interactions` | GET | Paginated list with filters |
| `/api/interactions/{id}` | GET | Full interaction detail with AI summary |
| `/api/interactions/{id}/related` | GET | Related interactions by mode |
| `/api/root_cause` | POST | Analyze interactions for root causes |
| `/api/metrics` | GET | Aggregated KPI metrics |
| `/api/trends` | GET | Time series data |
| `/api/breakdown` | GET | Grouped counts by dimension |
| `/api/agents/performance` | GET | Agent performance metrics |

## Data Model

### Taxonomy (Fixed)

**Tier 1 - Line of Business**: Retail Banking, Commercial Banking, Lending, Digital Banking, Wealth Management, Operations, Compliance, Other

**Tier 2 - Call Reason**: New Business, Existing Business, Account Maintenance, Payments & Transactions, Digital Access, Disputes & Issues, Information Request

**Tier 3 - Product**: ATM/Debit/Prepaid Card, Checking Account, Savings Account, Credit Card, Mortgage, HELOC/HELOAN, Auto Loan, Personal Unsecured Loan, Line of Credit, Commercial Loan/LOC, Merchant Solutions, Wealth Products, Facilities, Safe Deposit Box, Other

### Interaction Fields

- Basic: interaction_id, timestamp, channel, customer_segment
- Taxonomy: line_of_business, call_reason, product
- Agent: region, team_leader, agent_id, agent_name, tenure_band
- Metrics: handling_time_seconds, hold_time_seconds, transfer_count, escalated
- Resolution: resolved_on_first_contact, disposition
- Complaint: is_complaint, complaint_category, complaint_severity, complaint_text
- Digital: digital_eligible, deflection_attempted, deflection_success, digital_failure_reason
- Revenue: revenue_opportunity_flag, revenue_at_risk_flag, estimated_cost_dollars
- AI: root_cause_label, root_cause_confidence, recommended_actions

### Root Cause Categories

1. Policy/Fees Confusion
2. Digital/App Experience
3. Processing Delays
4. Incorrect Info / Agent Knowledge Gap
5. Fraud & Disputes
6. Documentation / KYC Friction
7. Service Experience

## Data Distribution

- ~11,000 interactions over 90 days
- ~23% complaint rate (higher for "problem agents")
- Complaints have higher handling time (6-30 min vs 2-12 min)
- Lower FCR for complaints (55% vs 78%)
- Weekend volume reduced to 40%
- 80 agents across 4 regions with 3-5 team leaders each

## Assumptions

1. Cost per minute assumed at $0.75 for estimated_cost_dollars calculation
2. Digital eligibility determined by product and call reason combinations
3. "Problem agents" (10% of agents) have 45% complaint rate vs 18% baseline
4. Root cause classification uses keyword matching on complaint_text
5. Agent concentration threshold is 40% (top 3 agents share) for "Agent-Concentrated" label
6. AI summaries are deterministically generated from interaction fields

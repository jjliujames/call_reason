"""
Fake data generator for Call Center Insights Dashboard.
Generates realistic interaction data for 90 days.
"""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from taxonomy import (
    LINES_OF_BUSINESS, CALL_REASONS, PRODUCTS, REGIONS, CHANNELS,
    CUSTOMER_SEGMENTS, TENURE_BANDS, DISPOSITIONS, COMPLAINT_CATEGORIES,
    COMPLAINT_SEVERITIES, DIGITAL_FAILURE_REASONS, LOB_TO_PRODUCTS,
    DIGITAL_ELIGIBLE_PRODUCTS, DIGITAL_ELIGIBLE_REASONS,
    PRODUCT_WEIGHTS, CALL_REASON_WEIGHTS, TEAM_LEADERS
)
from root_cause_engine import classify_interaction, generate_ai_summary

# Complaint text templates by category
COMPLAINT_TEMPLATES = {
    "Fees & Pricing": [
        "I was charged an overdraft fee but didn't expect it. No one explained the policy.",
        "The monthly fee is higher than what was quoted. Want a refund.",
        "Interest rate increased without notice. This feels deceptive.",
        "Why am I being charged for paper statements? I never agreed to this.",
        "The wire transfer fee is excessive compared to other banks.",
        "I was told this account had no fees but I'm seeing charges every month.",
        "Foreign transaction fees are ridiculous. Need to dispute these.",
        "Late payment fee applied even though I paid on time.",
    ],
    "Processing Delays": [
        "My deposit has been pending for 5 days. When will it clear?",
        "Loan approval is taking forever. Was told 2 days, it's been 2 weeks.",
        "Wire transfer should have arrived yesterday. Still waiting.",
        "Account opening is so slow. Why does this take so long?",
        "Been waiting 3 weeks for my new card.",
        "Mortgage application status hasn't updated in 10 days.",
        "Refund still pending after 2 weeks. Ridiculous.",
        "Credit limit increase request has been sitting for a month.",
    ],
    "Digital Experience": [
        "Mobile app keeps crashing when I try to deposit a check.",
        "Can't login to my account. App shows error every time.",
        "Password reset isn't working. Tried multiple times.",
        "OTP code never arrives. Been waiting 30 minutes.",
        "App is so slow it times out before I can finish.",
        "Got error during payment. Don't know if it went through.",
        "Login screen freezes on my phone. Very frustrating.",
        "Online banking has been down all day.",
    ],
    "Agent / Information Quality": [
        "Last agent told me something completely different.",
        "Given incorrect information about my balance. Called 3 times.",
        "Different answer every time I call. Staff needs training.",
        "Agent didn't know how to help with basic questions.",
        "Was told check would clear today but it didn't.",
        "Previous rep said fee would be waived. This one says no.",
        "Inconsistent answers from your team. Frustrating.",
        "Agent put me on hold 20 minutes just to give wrong info.",
    ],
    "Fraud & Disputes": [
        "Unauthorized charge on my account. Need it reversed now.",
        "Didn't make this purchase. Card information was stolen.",
        "Fraud alert locked my account but can't reach anyone.",
        "Chargeback filed 3 weeks ago. Still not resolved.",
        "Someone opened account in my name. Identity theft.",
        "Dispute process is too complicated. Sent docs twice.",
        "Unauthorized transaction keeps appearing after I reported it.",
        "Fraud claim denied but I have proof I didn't make purchase.",
    ],
    "Documentation / KYC": [
        "Uploaded ID three times. Why do you keep asking for it?",
        "Verification rejected my documents for no clear reason.",
        "KYC requirements excessive. Just want simple account.",
        "Document upload keeps failing on website.",
        "Why verify identity again? Been customer for years.",
        "ID verification couldn't read my license.",
        "Verification taking too long. Need account access now.",
        "Submitted all docs but account still restricted.",
    ],
    "Service Experience": [
        "Been on hold for 45 minutes. This is unacceptable.",
        "Transferred 4 times and still no resolution.",
        "Agent was rude and dismissive of my concerns.",
        "Promised callback but never received one.",
        "Disconnected after waiting 30 minutes. Called back, started over.",
        "Agent seemed rushed and didn't listen to my full issue.",
        "Had to repeat my problem to every person I spoke with.",
        "Wait times are always over 30 minutes. Need better staffing.",
    ]
}

AGENT_NOTES_TEMPLATES = [
    "Customer was understanding after explanation provided.",
    "Escalated to supervisor per customer request.",
    "Provided account credit as goodwill gesture.",
    "Referred to online FAQ resources.",
    "Scheduled callback for follow-up.",
    "Customer declined offered solutions.",
    "Issue requires branch visit to resolve.",
    "Sent confirmation email to customer.",
    "Created service ticket #{} for review.",
    "Customer satisfied with resolution.",
    "Advised on policy and next steps.",
    "Verified identity and processed request.",
    "Updated customer contact preferences.",
    "Explained digital self-service options.",
    "Documented issue for product team review.",
]

# First and last names for agent generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]


def generate_agents(count: int = 80) -> Tuple[List[Dict], Dict[str, Dict]]:
    """Generate agent roster with hierarchical structure."""
    agents = []
    agent_lookup = {}

    agents_per_region = count // len(REGIONS)

    for region in REGIONS:
        leaders = TEAM_LEADERS[region]
        for i in range(agents_per_region):
            agent_id = f"AGT{len(agents)+1:04d}"
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            agent_name = f"{first} {last}"
            team_leader = leaders[i % len(leaders)]
            tenure = random.choices(
                TENURE_BANDS,
                weights=[20, 35, 45]  # More experienced agents
            )[0]

            agent = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "team_leader": team_leader,
                "region": region,
                "tenure_band": tenure
            }
            agents.append(agent)
            agent_lookup[agent_id] = agent

    return agents, agent_lookup


def generate_interactions(
    agents: List[Dict],
    agent_lookup: Dict[str, Dict],
    num_days: int = 90,
    avg_per_day: int = 150
) -> List[Dict[str, Any]]:
    """Generate interaction records with realistic distributions."""
    interactions = []
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=num_days)

    # Create weighted lists for random selection
    weighted_products = []
    for product, weight in PRODUCT_WEIGHTS.items():
        weighted_products.extend([product] * int(weight * 10))

    weighted_reasons = []
    for reason, weight in CALL_REASON_WEIGHTS.items():
        weighted_reasons.extend([reason] * weight)

    # Identify "problem agents" for complaint concentration (10% of agents)
    problem_agents = random.sample([a["agent_id"] for a in agents], max(1, len(agents) // 10))

    current_date = start_date
    while current_date < end_date:
        # Vary volume by day of week
        day_of_week = current_date.weekday()
        if day_of_week >= 5:  # Weekend
            daily_count = int(avg_per_day * 0.4)
        else:
            daily_count = avg_per_day + random.randint(-30, 30)

        for _ in range(daily_count):
            interaction = _generate_single_interaction(
                current_date,
                agents,
                agent_lookup,
                weighted_products,
                weighted_reasons,
                problem_agents
            )
            interactions.append(interaction)

        current_date += timedelta(days=1)

    return interactions


def _generate_single_interaction(
    date: datetime,
    agents: List[Dict],
    agent_lookup: Dict[str, Dict],
    weighted_products: List[str],
    weighted_reasons: List[str],
    problem_agents: List[str]
) -> Dict[str, Any]:
    """Generate a single interaction record."""

    # Timestamp during business hours
    hour = random.randint(8, 19)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    timestamp = date.replace(hour=hour, minute=minute, second=second)

    # Select agent
    agent = random.choice(agents)
    agent_id = agent["agent_id"]
    agent_name = agent["agent_name"]
    team_leader = agent["team_leader"]
    region = agent["region"]
    tenure_band = agent["tenure_band"]

    # Product and call reason
    product = random.choice(weighted_products)
    call_reason = random.choice(weighted_reasons)

    # Line of business based on product
    lob = _get_lob_for_product(product)

    # Channel and segment
    channel = random.choices(CHANNELS, weights=[75, 25])[0]
    segment = random.choice(CUSTOMER_SEGMENTS)

    # Determine complaint status
    # Higher complaint rate for problem agents and certain combinations
    base_complaint_rate = 0.18
    if agent_id in problem_agents:
        base_complaint_rate = 0.45  # Problem agents have much higher complaint rates
    if call_reason == "Disputes & Issues":
        base_complaint_rate += 0.15
    if product in ["Credit Card", "Mortgage"]:
        base_complaint_rate += 0.05

    is_complaint = random.random() < min(base_complaint_rate, 0.6)

    # Complaint details
    complaint_category = None
    complaint_severity = None
    complaint_text = ""

    if is_complaint:
        complaint_category = random.choice(COMPLAINT_CATEGORIES)
        # Severity distribution
        complaint_severity = random.choices(
            COMPLAINT_SEVERITIES,
            weights=[50, 35, 15]  # More low severity
        )[0]
        # Get complaint text
        templates = COMPLAINT_TEMPLATES.get(complaint_category, COMPLAINT_TEMPLATES["Service Experience"])
        complaint_text = random.choice(templates)

    # Handling time (higher for complaints)
    if is_complaint:
        handling_time = random.randint(360, 1800)  # 6-30 min
    else:
        handling_time = random.randint(120, 720)   # 2-12 min

    # Hold time
    hold_time = random.randint(0, min(handling_time // 3, 600))

    # Transfers and escalation
    if is_complaint:
        transfer_count = random.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
        escalated = random.random() < 0.25
    else:
        transfer_count = random.choices([0, 1, 2], weights=[70, 25, 5])[0]
        escalated = random.random() < 0.08

    # Resolution
    if is_complaint:
        resolved_first = random.random() < 0.55
    else:
        resolved_first = random.random() < 0.78

    if resolved_first:
        disposition = "Resolved"
    elif escalated:
        disposition = "Escalated"
    else:
        disposition = random.choice(["Resolved", "Follow-up Required"])

    # Digital eligibility and deflection
    digital_eligible = (
        product in DIGITAL_ELIGIBLE_PRODUCTS and
        call_reason in DIGITAL_ELIGIBLE_REASONS
    )

    deflection_attempted = False
    deflection_success = False
    digital_failure_reason = None

    if digital_eligible:
        deflection_attempted = random.random() < 0.6
        if deflection_attempted:
            # Success rate varies by product/reason
            success_rate = 0.4
            if call_reason == "Digital Access":
                success_rate = 0.25  # Ironic - digital issues have lower digital success
            if is_complaint:
                success_rate = 0.2

            deflection_success = random.random() < success_rate
            if not deflection_success:
                digital_failure_reason = random.choice(DIGITAL_FAILURE_REASONS)

    # Revenue flags
    revenue_opportunity = random.random() < 0.15
    revenue_at_risk = is_complaint and complaint_severity == "High" and random.random() < 0.4

    # Estimated cost ($0.75/min assumed)
    estimated_cost = round(handling_time / 60 * 0.75, 2)

    # Agent notes
    agent_notes = ""
    if random.random() < 0.6:
        template = random.choice(AGENT_NOTES_TEMPLATES)
        if "{}" in template:
            agent_notes = template.format(random.randint(10000, 99999))
        else:
            agent_notes = template

    # Generate root cause analysis
    root_cause_data = classify_interaction(
        complaint_text=complaint_text if is_complaint else None,
        call_reason=call_reason,
        product=product,
        is_complaint=is_complaint
    )

    interaction = {
        "interaction_id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "channel": channel,
        "customer_segment": segment,
        "line_of_business": lob,
        "call_reason": call_reason,
        "product": product,
        "region": region,
        "team_leader": team_leader,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "tenure_band": tenure_band,
        "handling_time_seconds": handling_time,
        "hold_time_seconds": hold_time,
        "transfer_count": transfer_count,
        "escalated": escalated,
        "resolved_on_first_contact": resolved_first,
        "disposition": disposition,
        "is_complaint": is_complaint,
        "complaint_category": complaint_category,
        "complaint_severity": complaint_severity,
        "complaint_text": complaint_text,
        "agent_notes": agent_notes,
        "digital_eligible": digital_eligible,
        "deflection_attempted": deflection_attempted,
        "deflection_success": deflection_success,
        "digital_failure_reason": digital_failure_reason,
        "revenue_opportunity_flag": revenue_opportunity,
        "revenue_at_risk_flag": revenue_at_risk,
        "estimated_cost_dollars": estimated_cost,
        "root_cause_label": root_cause_data["root_cause_label"],
        "root_cause_confidence": root_cause_data["root_cause_confidence"],
        "recommended_actions": root_cause_data["recommended_actions"]
    }

    return interaction


def _get_lob_for_product(product: str) -> str:
    """Map product to most likely line of business."""
    for lob, products in LOB_TO_PRODUCTS.items():
        if product in products:
            return lob
    return "Other"


# Generate data at module load
AGENTS, AGENT_LOOKUP = generate_agents(80)
INTERACTIONS = generate_interactions(AGENTS, AGENT_LOOKUP, num_days=90, avg_per_day=150)

# Create index for fast lookup
INTERACTION_INDEX = {i["interaction_id"]: i for i in INTERACTIONS}


def get_all_agents() -> List[Dict]:
    return AGENTS


def get_agent_lookup() -> Dict[str, Dict]:
    return AGENT_LOOKUP


def get_all_interactions() -> List[Dict]:
    return INTERACTIONS


def get_interaction_by_id(interaction_id: str) -> Dict:
    return INTERACTION_INDEX.get(interaction_id)


def get_interaction_index() -> Dict[str, Dict]:
    return INTERACTION_INDEX

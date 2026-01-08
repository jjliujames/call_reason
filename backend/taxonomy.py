"""
Taxonomy definitions - DO NOT CHANGE per spec.
"""

# Tier 1 — Line of Business
LINES_OF_BUSINESS = [
    "Retail Banking",
    "Commercial Banking",
    "Lending",
    "Digital Banking",
    "Wealth Management",
    "Operations",
    "Compliance",
    "Other"
]

# Tier 2 — Call Reason
CALL_REASONS = [
    "New Business",
    "Existing Business",
    "Account Maintenance",
    "Payments & Transactions",
    "Digital Access",
    "Disputes & Issues",
    "Information Request"
]

# Tier 3 — Product
PRODUCTS = [
    "ATM / Debit / Prepaid Card",
    "Checking Account",
    "Savings Account",
    "Credit Card",
    "Mortgage",
    "HELOC / HELOAN",
    "Auto Loan",
    "Personal Unsecured Loan",
    "Line of Credit (including ODP)",
    "Commercial Loan / LOC",
    "Merchant Solutions",
    "Wealth Products",
    "Facilities",
    "Safe Deposit Box",
    "Other"
]

REGIONS = ["East", "West", "Central", "Atlantic"]

# Team leaders per region
TEAM_LEADERS = {
    "East": ["Sarah Johnson", "Michael Chen", "Emily Davis", "Robert Wilson"],
    "West": ["Jennifer Lopez", "David Kim", "Amanda Brown", "Christopher Lee"],
    "Central": ["Michelle Taylor", "James Anderson", "Lisa Martinez", "Kevin Thomas"],
    "Atlantic": ["Rachel Green", "Daniel White", "Nicole Harris", "Brandon Clark"]
}

CHANNELS = ["Phone", "Chat"]

CUSTOMER_SEGMENTS = ["Mass", "Affluent", "Small Business"]

TENURE_BANDS = ["< 6 months", "6–24 months", "2+ years"]

DISPOSITIONS = ["Resolved", "Follow-up Required", "Escalated"]

COMPLAINT_CATEGORIES = [
    "Fees & Pricing",
    "Processing Delays",
    "Digital Experience",
    "Agent / Information Quality",
    "Fraud & Disputes",
    "Documentation / KYC",
    "Service Experience"
]

COMPLAINT_SEVERITIES = ["Low", "Medium", "High"]

DIGITAL_FAILURE_REASONS = [
    "No self-serve available",
    "UX error",
    "Customer preference",
    "Authentication failed",
    "Policy requires agent"
]

# Mapping for realistic data distribution
LOB_TO_PRODUCTS = {
    "Retail Banking": ["Checking Account", "Savings Account", "ATM / Debit / Prepaid Card", "Credit Card", "Safe Deposit Box"],
    "Commercial Banking": ["Commercial Loan / LOC", "Merchant Solutions", "Checking Account"],
    "Lending": ["Mortgage", "HELOC / HELOAN", "Auto Loan", "Personal Unsecured Loan", "Line of Credit (including ODP)"],
    "Digital Banking": ["ATM / Debit / Prepaid Card", "Checking Account", "Savings Account", "Credit Card"],
    "Wealth Management": ["Wealth Products"],
    "Operations": ["Facilities", "Safe Deposit Box", "Other"],
    "Compliance": ["Other"],
    "Other": ["Other"]
}

# Products that are commonly digital-eligible
DIGITAL_ELIGIBLE_PRODUCTS = [
    "ATM / Debit / Prepaid Card",
    "Checking Account",
    "Savings Account",
    "Credit Card"
]

# Call reasons that commonly have digital options
DIGITAL_ELIGIBLE_REASONS = [
    "Digital Access",
    "Account Maintenance",
    "Payments & Transactions",
    "Information Request"
]

# Product weights for realistic distribution
PRODUCT_WEIGHTS = {
    "ATM / Debit / Prepaid Card": 18,
    "Checking Account": 22,
    "Savings Account": 10,
    "Credit Card": 20,
    "Mortgage": 8,
    "HELOC / HELOAN": 4,
    "Auto Loan": 5,
    "Personal Unsecured Loan": 4,
    "Line of Credit (including ODP)": 3,
    "Commercial Loan / LOC": 2,
    "Merchant Solutions": 1,
    "Wealth Products": 1,
    "Facilities": 1,
    "Safe Deposit Box": 0.5,
    "Other": 0.5
}

# Call reason weights
CALL_REASON_WEIGHTS = {
    "New Business": 10,
    "Existing Business": 25,
    "Account Maintenance": 20,
    "Payments & Transactions": 18,
    "Digital Access": 12,
    "Disputes & Issues": 10,
    "Information Request": 5
}

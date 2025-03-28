REQUIRED_COLUMNS = [
    "credit_score",
    "loan_amount",
    "property_value",
    "annual_income",
    "debt_amount",
    "loan_type",
    "property_type",
]

VALIDATION_RULES = {
    "credit_score": {"dtype": int, "range": (300, 850)},
    "loan_amount": {
        "dtype": (float, int),
        # loan amount should min 1 to consider it as mortgage
        "min": 1,
    },
    "property_value": {
        "dtype": (float, int),
        # must be greater than 0 to calculate LTV
        "min": 1,
    },
    "annual_income": {
        "dtype": (float, int),
        # must be greater than 0 to calculate DTI
        "min": 1,
    },
    "debt_amount": {
        "dtype": (float, int),
        "min": 0,
    },
    "loan_type": {
        "dtype": object,
        "options": ["adjustable", "fixed"],
    },
    "property_type": {
        "dtype": object,
        "options": ["single_family", "condo"],
    },
}

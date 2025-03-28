import json
import pandas as pd
import numpy as np


def validate_inputs(df):
    """Validates the dataframe input"""
    validation_rules = {
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

    # check if any column is missing
    missing_columns = [
        column for column in validation_rules if column not in df.columns
    ]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    # validate each column as defined in rules above
    for column, rule in validation_rules.items():
        # validate all rows follow the datatype
        valid = df[column].apply(lambda x: isinstance(x, rule["dtype"])).all()
        if not valid:
            raise ValueError(f"Column {column} contains invalid data types")

        # check min value for columns if applicable
        if "min" in rule:
            below_min = df[column] < rule["min"]
            if below_min.any():
                raise ValueError(
                    f"Column {column} contains values lower than min allowed"
                )

        # check range for columns is applicable
        if "range" in rule:
            allowed_min = rule["range"][0]
            allowed_max = rule["range"][1]
            if df[column].min() < allowed_min or df[column].max() > allowed_max:
                raise ValueError(f"Column {column} contains out of range values")

        # check options for columns if applicable
        if "options" in rule:
            valid_options = df[column].isin(rule["options"])
            if not valid_options.all():
                raise ValueError(f"Column {column} contains invalid values")

    # check for business logic validation
    # loan amount must be lower than property value
    loan_invalidations = df["loan_amount"] > df["property_value"]
    if loan_invalidations.any():
        raise ValueError(
            "Some mortgages have invalid combination of loan amount and property values"
        )


def calculate_rmbs_ratings(input_file):
    """Calculate RMBS ratings for given input file"""

    # Read input file
    with open(input_file) as file:
        data = json.load(file)

    # Convert json obj to dataframe
    df = pd.DataFrame(data["mortgages"])


    # Validate input data
    validate_inputs(df)

    # set calculated fields
    df["ltv"] = (df["loan_amount"] / df["property_value"]) * 100
    df["dti"] = (df["debt_amount"] / df["annual_income"]) * 100

    df["risk_score"] = 0

    # ltv impact on risk score
    df["risk_score"] += np.where(
        df["ltv"] > 90,
        2,
        np.where(df["ltv"] > 80, 1, 0),
    )

    # dti impact on risk score
    df["risk_score"] += np.where(
        df["dti"] > 50,
        2,
        np.where(df["dti"] > 40, 1, 0),
    )

    # credit score impact
    df["risk_score"] += np.where(
        df["credit_score"] >= 700,
        -1,
        np.where(df["credit_score"] < 650, 1, 0),
    )

    # loan type impact
    df["credit_score"] += np.where(df["loan_type"] == "fixed", -1, 1)

    # property type impact
    df["credit_score"] += np.where(
        df["property_type"] == "single_family",
        0,
        1,
    )

    # calculate total risk score
    total_risk_score = df["risk_score"].sum()

    avg_credit_score = df["credit_score"].mean()
    if avg_credit_score >= 700:
        total_risk_score -= 1
    elif avg_credit_score < 650:
        total_risk_score += 1

    # calculate final rating
    if total_risk_score <= 2:
        return "AAA"
    elif 3 <= total_risk_score <= 5:
        return "BBB"
    return "C"


if __name__ == "__main__":
    input_file_name = "input.json"
    rating = calculate_rmbs_ratings(input_file=input_file_name)
    print(f"Final rating is {rating}")

import json
import pandas as pd
import numpy as np
import constants


def validate_exact_columns(df):
    """Validates the dataframe has exactly the specified columns"""
    actual_columns = set(df.columns)
    required_columns = set(constants.REQUIRED_COLUMNS)

    extra_columns = actual_columns - required_columns
    missing_columns = required_columns - actual_columns
    if extra_columns:
        raise ValueError(f"Extra columns in the input: {extra_columns}")
    if missing_columns:
        raise ValueError(f"Missing columns in the input: {missing_columns}")


def validate_inputs(df):
    """Validates the dataframe input"""

    # validate any missing keys in any rows
    has_nans = df.isna().any().any()
    if has_nans:
        raise ValueError("Some keys are missing in json obj")

    # Validate exact columns
    validate_exact_columns(df)

    # check if any column is missing
    missing_columns = [
        column for column in constants.VALIDATION_RULES if column not in df.columns
    ]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    # validate each column as defined in rules above
    for column, rule in constants.VALIDATION_RULES.items():
        # validate all rows follow the datatype
        valid = (
            df[column]
            .apply(
                lambda x: isinstance(
                    x,
                    rule["dtype"],
                )
            )
            .all()
        )
        if not valid:
            raise ValueError(f"Column {column} contains invalid data types")

        # check min value for columns if applicable
        if "min" in rule:
            below_min = df[column] < rule["min"]
            if below_min.any():
                raise ValueError(
                    f"Column {column} contains values lower than allowed minimum"
                )

        # check range for columns is applicable
        if "range" in rule:
            allowed_min = rule["range"][0]
            allowed_max = rule["range"][1]
            if df[column].min() < allowed_min or df[column].max() > allowed_max:
                raise ValueError(f"Column {column} values higher than allowed maximum")

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
    return 0


def calculate_credit_rating(df):
    """Calculate RMBS ratings for given input file"""

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
    df["risk_score"] += np.where(df["loan_type"] == "fixed", -1, 1)

    # property type impact
    df["risk_score"] += np.where(
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
    # Read input file
    with open(input_file_name) as file:
        data = json.load(file)

    # Convert json obj to dataframe
    df = pd.DataFrame(data["mortgages"])
    rating = calculate_credit_rating(df)
    print(f"Final rating is {rating}")

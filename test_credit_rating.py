import unittest
import json
import pandas as pd
from credit_rating import validate_inputs, calculate_rmbs_ratings


class TestCreditRating(unittest.TestCase):
    """Unit tests for credit rating calculation logic"""

    def setUp(self):
        """Implement common logic before every test method invocation"""
        return super().setUp()

    def test_valid_data(self):
        """Tests valid mortgages data"""
        with open("input.json") as file:
            data = json.load(file)
        df = pd.DataFrame(data["mortgages"])
        validation_result = validate_inputs(df)
        assert validation_result == 0, "Input validation test case failed"

    def test_missing_column_in_some_rows(self):
        """Tests scenario where some of the mortgages have some missing keys"""
        with open("input.json") as file:
            data = json.load(file)
        # delete a key from one of mortgages to mimick missing column
        del data["mortgages"][0]["annual_income"]
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "Some keys are missing in json obj",
            str(exception.exception),
        )

    def test_extra_column(self):
        """Tests if all mortgages have extra keys which are not required"""
        with open("input.json") as file:
            data = json.load(file)
        # add an extra key to every mortgage to mimick extra column
        data["mortgages"][0]["annual_income1"] = 100
        data["mortgages"][1]["annual_income1"] = 100
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "Extra columns in the input",
            str(exception.exception),
        )

    def test_missing_column(self):
        """Tests if all mortgages have some required keys missing"""
        with open("input.json") as file:
            data = json.load(file)
        # remove some required key from every mortgage to mimick missing column
        del data["mortgages"][0]["annual_income"]
        del data["mortgages"][1]["annual_income"]
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "Missing columns in the input",
            str(exception.exception),
        )

    def test_invalid_datatype(self):
        """Tests if any key is assigned incorrect data types"""
        with open("input.json") as file:
            data = json.load(file)
        # provide incorrect data to some column
        data["mortgages"][1]["annual_income"] = "temp"
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "contains invalid data",
            str(exception.exception),
        )

    def test_min_value(self):
        """Tests if any key has value which is lower than allowed"""
        with open("input.json") as file:
            data = json.load(file)
        # provide out of range value to some columns
        data["mortgages"][1]["annual_income"] = -1000
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "lower than allowed minimum",
            str(exception.exception),
        )

    def test_max_value(self):
        """Tests if any keys has value which is higher than allowed"""
        with open("input.json") as file:
            data = json.load(file)
        # provide out of range value to some columns
        data["mortgages"][1]["credit_score"] = 1000
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "higher than allowed maximum",
            str(exception.exception),
        )

    def test_invalid_value(self):
        """Tests if any keys have values which are not allowed"""
        with open("input.json") as file:
            data = json.load(file)
        # provide unexpected value to some columns
        data["mortgages"][1]["property_type"] = "studio"
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "contains invalid values",
            str(exception.exception),
        )

    def test_ltv_calc(self):
        """Tests basic LTV should be lower than equal to 100%"""
        with open("input.json") as file:
            data = json.load(file)
        # provide loan amount more than property value
        data["mortgages"][1]["loan_amount"] = 1000
        data["mortgages"][1]["property_value"] = 100
        df = pd.DataFrame(data["mortgages"])
        with self.assertRaises(ValueError) as exception:
            validate_inputs(df)
        self.assertIn(
            "invalid combination of loan amount and property values",
            str(exception.exception),
        )

    def test_correct_risk_score(self):
        """Tests a valid scenario and compares the credit rating"""
        df = pd.DataFrame(
            {
                "credit_score": [725],  # Should give -1 (>=700)
                "loan_amount": [170000],
                "property_value": [200000],  # LTV = 85% -> +1 points
                "annual_income": [100000],
                "debt_amount": [60000],  # DTI = 60% -> +2 points
                "loan_type": ["adjustable"],  # +1 point
                "property_type": ["condo"],  # +1 point
            }
        )

        # Expected manual calculation:
        # -1 (credit) + 1 (LTV) + 2 (DTI) + 1 (loan type) + 1 (property) + (-1) (average credit score) = 3

        result = calculate_rmbs_ratings(df)
        self.assertEqual(result, "BBB")  # Since 3 is in 3-5 BBB range

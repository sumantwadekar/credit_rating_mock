# RMBS Credit Rating Calculator

## Overview
A Python implementation for calculating credit ratings of Residential Mortgage-Backed Securities (RMBS) based on underlying mortgage characteristics. The solution includes:
- Data validation pipeline
- Risk score calculation engine
- Comprehensive test suite

### Installation
```bash
git clone https://github.com/sumantwadekar/credit_rating_mock.git
cd credit_rating_mock
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Logic

### 1. Core Functions

#### `validate_exact_columns(df)`
- Validates DataFrame contains exactly the required columns
- Checks for:
  - Extra columns not in `constants.REQUIRED_COLUMNS`
  - Missing required columns
- Raises `ValueError` with detailed message on failure

#### `validate_inputs(df)`
- Performs comprehensive data validation:
  1. Checks for NaN values in any field
  2. Validates column structure via `validate_exact_columns()`
  3. Enforces data type rules from `constants.VALIDATION_RULES`
  4. Validates value ranges and allowed options
  5. Verifies business rules (e.g., LTV ≤ 100%)

#### `calculate_credit_rating(df)`
- Main calculation pipeline:
  1. Validates input data
  2. Computes LTV and DTI ratios
  3. Calculates risk score based on:
     - Credit scores
     - Loan characteristics
     - Property types
  4. Adjusts score based on average credit
  5. Returns final rating (AAA, BBB, or C)

### 2. Risk Calculation Methodology

| Factor | Calculation | Points |
|--------|-------------|--------|
| **LTV Ratio** | >90%: +2, >80%: +1 | 0-2 |
| **DTI Ratio** | >50%: +2, >40%: +1 | 0-2 |
| **Credit Score** | ≥700: -1, <650: +1 | -1/0/+1 |
| **Loan Type** | Fixed: -1, Adjustable: +1 | -1/+1 |
| **Property Type** | Single Family: 0, Condo: +1 | 0/+1 |
| **Avg Credit Score** | ≥700: -1, <650: +1 | -1/0/+1 |

**Final Rating:**
- AAA: Total Score ≤ 2
- BBB: Total Score 3-5
- C: Total Score > 5

## Test Suite

### Validation Tests
| Test Case | Description | Verification |
|-----------|-------------|--------------|
| `test_valid_data` | Standard valid input | Returns 0 |
| `test_missing_column*` | Missing required fields | Raises ValueError |
| `test_invalid_datatype` | Incorrect data types | Detects invalid data |

### Calculation Tests
| Test Case | Scenario | Expected Rating |
|-----------|----------|-----------------|
| `test_correct_risk_score` | Mixed risk factors (Score=3) | BBB |
| `test_credit_score_lt_650` | Poor credit (Score=7) | C |
| `test_credit_score_in_650_to_700` | Medium credit (Score=1) | AAA |


## Technical decisions

### Validations

#### Schema, values and business rules validation
#### Parallelized validation for large datasets can be done using chunk processing
#### Meaningful error messages

## Calculations

#### Vectorized calculations using numpy
#### memory efficient processing

## Scopes

#### Multiple customers having variable number mortgages using batches

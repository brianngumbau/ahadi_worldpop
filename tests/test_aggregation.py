"""
Unit tests for demographic indicator calculations and output schema integrity.
"""
import os
import pandas as pd
import pytest

PROCESSED_CSV = os.path.join("data", "processed", "kenya_population_by_county.csv")

@pytest.fixture
def df():
    assert os.path.exists(PROCESSED_CSV), "Processed CSV does not exist."
    return pd.read_csv(PROCESSED_CSV)

def test_required_columns_present(df):
    """Verify primary dataset schema conforms to Requirement 1.4."""
    required_cols = [
        'county', 'year', 'total_population', 'children_under_5',
        'working_age', 'elderly_65plus', 'sex_ratio', 'dependency_ratio',
        'child_dependency_ratio', 'elderly_dependency_ratio',
        'pct_children', 'pct_elderly'
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

def test_non_negative_values(df):
    """Ensure demographic aggregates contain no negative values."""
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        assert (df[col] >= 0).all(), f"Found negative values in {col}"

def test_dependency_ratio_logic(df):
    """Verify dependency ratio formula: (children + elderly) / working_age * 100."""
    sample = df[df['working_age'] > 0].iloc[0]
    expected_ratio = round(((sample['children_under_5'] + sample['elderly_65plus']) / sample['working_age']) * 100, 2)
    assert sample['dependency_ratio'] == pytest.approx(expected_ratio, rel=1e-2)

def test_proportion_bounds(df):
    """Verify percentage proportions do not exceed 100%."""
    assert (df['pct_children'] <= 100).all(), "pct_children exceeds 100%"
    assert (df['pct_elderly'] <= 100).all(), "pct_elderly exceeds 100%"
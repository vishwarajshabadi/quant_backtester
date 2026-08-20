import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from backtester.metrics import PerformanceEngine


def test_max_drawdown():
    equity = pd.Series([100.0, 110.0, 99.0, 120.0])
    expected_mdd = -0.10  # (99 - 110) / 110

    assert np.isclose(PerformanceEngine.max_drawdown(equity), expected_mdd)


def test_sharpe_ratio_zero_volatility():
    equity = pd.Series([100.0, 100.0, 100.0, 100.0])
    assert PerformanceEngine.sharpe_ratio(equity) == 0.0


def test_historical_var():
    equity = pd.Series([100.0, 101.0, 102.0, 99.96])
    var_95 = PerformanceEngine.historical_var(equity, confidence=0.95)

    assert var_95 < 0.0
    assert pytest.approx(var_95, abs=0.01) == -0.02

import numpy as np
import pandas as pd
import pytest

from backtester.metrics import PerformanceEngine


def test_max_drawdown():
    equity = pd.Series([100.0, 110.0, 99.0, 120.0])
    expected_mdd = -0.10  # (99 - 110) / 110

    assert np.isclose(PerformanceEngine.max_drawdown(equity), expected_mdd)


def test_sharpe_ratio_zero_volatility():
    equity = pd.Series([100.0, 100.0, 100.0, 100.0])
    assert PerformanceEngine.sharpe_ratio(equity) == 0.0


def test_sortino_ratio():
    equity = pd.Series([100.0, 102.0, 100.98, 104.01, 101.93])

    expected = (0.005 / np.sqrt((0.01**2 + 0.02**2) / 4)) * np.sqrt(252)
    assert PerformanceEngine.sortino_ratio(equity) == pytest.approx(expected, rel=1e-3)


def test_historical_var():
    equity = pd.Series([100.0, 101.0, 102.0, 99.96])
    var_95 = PerformanceEngine.historical_var(equity, confidence=0.95)

    assert var_95 < 0.0
    assert pytest.approx(var_95, abs=0.01) == -0.02

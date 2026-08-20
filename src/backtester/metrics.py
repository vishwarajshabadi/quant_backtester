# risk and performance metrics

import numpy as np
import pandas as pd


class PerformanceEngine:
    @staticmethod
    def calculate_returns(equity: pd.Series) -> pd.Series:
        return (
            equity.squeeze().pct_change().dropna()
            if isinstance(equity, pd.DataFrame)
            else equity.pct_change().dropna()
        )

    @classmethod
    def sharpe_ratio(
        cls, equity: pd.Series, risk_free_rate: float = 0.0, periods: int = 252
    ) -> float:
        rets = cls.calculate_returns(equity)
        if rets.empty or (vol := float(rets.std(ddof=1))) == 0 or np.isnan(vol):
            return 0.0
        return float(
            ((rets.mean() - (risk_free_rate / periods)) / vol) * np.sqrt(periods)
        )

    @classmethod
    def sortino_ratio(
        cls, equity: pd.Series, risk_free_rate: float = 0.0, periods: int = 252
    ) -> float:
        rets = cls.calculate_returns(equity)
        if rets.empty:
            return 0.0

        excess = rets - (risk_free_rate / periods)
        downside = excess[excess < 0]

        if (
            downside.empty
            or (down_vol := float(downside.std(ddof=1))) == 0
            or np.isnan(down_vol)
        ):
            return 0.0
        return float((excess.mean() / down_vol) * np.sqrt(periods))

    @staticmethod
    def max_drawdown(equity: pd.Series) -> float:
        if equity.empty:
            return 0.0
        return float(((equity - equity.cummax()) / equity.cummax()).min())

    @classmethod
    def historical_var(cls, equity: pd.Series, confidence: float = 0.95) -> float:
        rets = cls.calculate_returns(equity)
        return (
            float(np.percentile(rets, (1.0 - confidence) * 100))
            if not rets.empty
            else 0.0
        )

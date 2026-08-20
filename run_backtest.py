# main

import os
import sys
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from backtester.data import YFinanceDataHandler
from backtester.strategy import MovingAverageCrossoverStrategy
from backtester.portfolio import Portfolio
from backtester.execution import SimulatedExecutionHandler
from backtester.engine import BacktestEngine
from backtester.metrics import PerformanceEngine
from backtester.trade_logger import TradeLogger


def main():
    start_date, end_date = "2020-01-01", "2023-12-31"
    initial_capital = 100_000.0

    engine = BacktestEngine(
        data_handler=YFinanceDataHandler(["AAPL", "MSFT"], start_date, end_date),
        strategy=MovingAverageCrossoverStrategy(fast_window=20, slow_window=50),
        portfolio=Portfolio(initial_capital=initial_capital),
        execution_handler=SimulatedExecutionHandler(
            commission_rate=0.0005, slippage_pct=0.0002
        ),
        trade_logger=TradeLogger(),
    )

    engine.run()

    equity_df = engine.portfolio.get_equity_curve()
    total_equity = equity_df["total_equity"]

    sp500_data = yf.download("^GSPC", start=start_date, end=end_date, progress=False)
    sp500 = (
        sp500_data["Close"].squeeze()
        if isinstance(sp500_data, pd.DataFrame)
        else sp500_data
    )
    sp500_normalized = (sp500 / sp500.iloc[0]) * initial_capital

    def calc_metrics(series):
        return {
            "return": (series.iloc[-1] / initial_capital - 1) * 100,
            "mdd": PerformanceEngine.max_drawdown(series) * 100,
            "sharpe": PerformanceEngine.sharpe_ratio(series),
            "sortino": PerformanceEngine.sortino_ratio(series),
            "var_95": PerformanceEngine.historical_var(series) * 100,
        }

    strat_metrics = calc_metrics(total_equity)
    bench_metrics = calc_metrics(sp500_normalized)

    print("\n--- PERFORMANCE TEAR SHEET ---")
    print(f"{'Metric':<24}{'Strategy':>14}{'S&P 500 Benchmark':>24}")
    print("-" * 62)
    print(
        f"{'Total Return':<24}{strat_metrics['return']:>13.2f}%{bench_metrics['return']:>23.2f}%"
    )
    print(
        f"{'Max Drawdown':<24}{strat_metrics['mdd']:>13.2f}%{bench_metrics['mdd']:>23.2f}%"
    )
    print(
        f"{'Sharpe Ratio':<24}{strat_metrics['sharpe']:>13.2f}{bench_metrics['sharpe']:>24.2f}"
    )
    print(
        f"{'Sortino Ratio':<24}{strat_metrics['sortino']:>13.2f}{bench_metrics['sortino']:>24.2f}"
    )
    print(
        f"{'VaR (95%)':<24}{strat_metrics['var_95']:>13.2f}%{bench_metrics['var_95']:>23.2f}%"
    )

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]}, sharex=True
    )

    ax.plot(total_equity.index, total_equity, label="Strategy", color="blue")
    ax.plot(
        sp500_normalized.index,
        sp500_normalized,
        label="S&P 500",
        color="orange",
        linestyle="--",
    )
    ax.set(
        title="Strategy Performance vs. S&P 500 Benchmark", ylabel="Portfolio Value ($)"
    )
    ax.legend(loc="upper left")

    strat_dd = (total_equity / total_equity.cummax() - 1) * 100
    bench_dd = (sp500_normalized / sp500_normalized.cummax() - 1) * 100

    ax2.fill_between(
        strat_dd.index,
        strat_dd,
        0,
        where=strat_dd < 0,
        color="blue",
        alpha=0.25,
        label="Strategy Drawdown",
    )
    ax2.plot(
        bench_dd.index,
        bench_dd,
        label="S&P 500 Drawdown",
        color="orange",
        linestyle="--",
    )
    ax2.set(ylabel="Drawdown (%)", xlabel="Date")
    ax2.legend(loc="upper left")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    engine.trade_logger.print_trade_book()


if __name__ == "__main__":
    main()

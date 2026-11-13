# Backtest — Key Functions
# Shows: commission/slippage modeling, gap vs intraday stop logic

from dataclasses import dataclass
from typing import Optional


@dataclass
class Trade:
    symbol: str
    side: str          # "BUY" or "SELL"
    qty: float
    ref_price: float   # price before costs
    fill_price: float  # price after costs
    fee: float
    slippage_cost: float


def simulate_fill(
    ref_price: float,
    side: str,
    fee_bps: float,
    slippage_bps: float,
    qty: float,
) -> Trade:
    """Simulate order fill with commission and slippage."""
    fee_rate = fee_bps / 10_000.0
    slip_rate = slippage_bps / 10_000.0

    if side == "BUY":
        fill = ref_price * (1.0 + slip_rate)
        slippage_cost = qty * (fill - ref_price)
    else:
        fill = ref_price * (1.0 - slip_rate)
        slippage_cost = qty * (ref_price - fill)

    fee = qty * fill * fee_rate
    return Trade(
        symbol="", side=side, qty=qty,
        ref_price=ref_price, fill_price=fill,
        fee=fee, slippage_cost=slippage_cost,
    )


def check_stop(bar: dict, stop_price: float) -> Optional[str]:
    """Check if stop was hit. Returns 'GAP_STOP', 'INTRADAY_STOP', or None."""
    open_price = bar["o"]
    low = bar["l"]

    if open_price < stop_price:
        return "GAP_STOP"       # opened below stop
    if low <= stop_price:
        return "INTRADAY_STOP"  # touched stop during session
    return None


def stop_fill_price(stop_price: float, stop_type: str, slippage_bps: float) -> float:
    """Fill price depends on stop type."""
    slip_rate = slippage_bps / 10_000.0
    # Both types fill at stop price with slippage
    return stop_price * (1.0 - slip_rate)


# Example usage:
# trade = simulate_fill(100.0, "BUY", fee_bps=10, slippage_bps=5, qty=10.0)
# print(f"Fill: {trade.fill_price}, Fee: ${trade.fee:.2f}, Slip: ${trade.slippage_cost:.2f}")

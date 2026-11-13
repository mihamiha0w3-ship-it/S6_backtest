# Trading Bot — Key Functions
# Shows: order confirmation, argument parsing

import uuid
import time
from dataclasses import dataclass, field
from html import escape


@dataclass
class PendingOrder:
    """Order awaiting user confirmation."""
    token: str
    user_id: int
    side: str
    symbol: str
    amount: float | None
    quote_amount: float | None
    order_type: str
    price: float | None
    created_at: float = field(default_factory=time.time)

    def describe(self) -> str:
        size = (f"{self.quote_amount:g} USDT (at market)" if self.quote_amount
                else f"{self.amount:g} {self.symbol.split('/')[0]}")
        price = f" @ {self.price:g}" if self.price else " at market price"
        return (f"<b>{self.order_type.upper()} {self.side.upper()}</b> "
                f"<code>{escape(self.symbol)}</code>\nSize: {size}{price}")


def parse_order_args(text: str, *, need_price: bool) -> tuple:
    """Parse '<side> <symbol> <amount|quote:N> [price]'.

    Examples:
        "buy BTC/USDT 0.001 58000" -> ("buy", "BTC/USDT", 0.001, None, 58000.0)
        "buy BTC/USDT quote:20" -> ("buy", "BTC/USDT", None, 20.0, None)
    """
    parts = (text or "").split()
    if len(parts) < (4 if need_price else 3):
        raise ValueError("not enough arguments")

    side, symbol = parts[0].lower(), parts[1].upper()
    raw_amount, price = parts[2], None
    quote_amount, amount = None, None

    if raw_amount.lower().startswith("quote:"):
        quote_amount = float(raw_amount.split(":", 1)[1])
    else:
        amount = float(raw_amount)

    if need_price:
        price = float(parts[3])

    return side, symbol, amount, quote_amount, price


async def on_confirm(pending: PendingOrder, client) -> dict:
    """Submit confirmed order to exchange via CCXT."""
    if pending.order_type == "limit":
        return await client.place_limit_order(
            pending.side, pending.symbol,
            pending.amount or 0.0, pending.price or 0.0,
        )
    return await client.place_market_order(
        pending.side, pending.symbol, pending.amount or 0.0,
    )


# Example usage:
# side, symbol, amount, quote, price = parse_order_args("buy BTC/USDT 0.001 58000", need_price=True)
# pending = PendingOrder(token=uuid.uuid4().hex[:10], user_id=123, side=side, symbol=symbol,
#                        amount=amount, quote_amount=quote, order_type="limit", price=price)
# result = await on_confirm(pending, client)

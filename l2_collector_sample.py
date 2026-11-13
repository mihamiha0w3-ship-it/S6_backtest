# L2 Order Book Collector (Python) — Key Function
# Shows: snapshot + delta parsing, seqId gap detection

MAX_DEPTH = 400


class OrderBook:
    """Parses OKX books channel: snapshot + incremental deltas."""

    def __init__(self):
        self.bids, self.asks = {}, {}     # price(float) -> size(float)
        self.seq, self.synced = 0, False

    def apply(self, rec: dict) -> tuple:
        """Parse one record from books channel.

        Returns (ok: bool, kind: str) where kind is 'snapshot', 'delta', or 'gap'.
        """
        bids, asks = rec.get("bids") or [], rec.get("asks") or []
        seq, prev = int(rec.get("seqId", 0)), int(rec.get("prevSeqId", 0))

        # First message or large message = snapshot (full reload)
        is_snap = not self.synced or (len(bids) >= MAX_DEPTH and len(asks) >= MAX_DEPTH)
        if is_snap:
            self.bids = {float(p): float(s) for p, s, *_ in bids}
            self.asks = {float(p): float(s) for p, s, *_ in asks}
            self.synced, self.seq = True, seq
            return True, "snapshot"

        # Check sequence gap — book is invalid, need resync
        if prev and self.seq and prev != self.seq:
            self.synced, self.seq = False, seq
            return False, "gap"

        # Apply incremental delta
        for p, s, *_ in bids:
            if float(s) == 0:
                self.bids.pop(float(p), None)  # remove level
            else:
                self.bids[float(p)] = float(s)  # add/update level

        for p, s, *_ in asks:
            if float(s) == 0:
                self.asks.pop(float(p), None)
            else:
                self.asks[float(p)] = float(s)

        self.seq = seq
        return True, "delta"

    def best(self) -> tuple:
        """Return (best_bid, best_ask) or (None, None)."""
        return (max(self.bids, default=None), min(self.asks, default=None))


# Example usage:
# book = OrderBook()
# ok, kind = book.apply({"bids": [["68863.5", "0.1"]], "asks": [["68864.0", "0.2"]], "seqId": 1})
# print(f"{kind}: best={book.best()}")

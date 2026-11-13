// L2 Order Book Collector (Rust) — Key Function
// Shows: snapshot + delta parsing, seqId gap detection

pub struct OrderBook {
    bids: Vec<(f64, f64)>,  // (price, size)
    asks: Vec<(f64, f64)>,
    seq: u64,
    synced: bool,
}

impl OrderBook {
    pub fn new() -> Self {
        Self {
            bids: vec![],
            asks: vec![],
            seq: 0,
            synced: false,
        }
    }

    /// Parse one record from OKX books channel.
    /// Returns "snapshot", "delta", or "gap".
    pub fn apply(&mut self, bids: &[(f64, f64)], asks: &[(f64, f64)], seq: u64) -> &'static str {
        // First message or large message = snapshot (full reload)
        if !self.synced || bids.len() >= 50 {
            self.bids = bids.to_vec();
            self.asks = asks.to_vec();
            self.synced = true;
            self.seq = seq;
            return "snapshot";
        }

        // Check sequence gap — book is invalid, need resync
        if self.seq > 0 && seq != self.seq + 1 {
            self.synced = false;
            return "gap";
        }

        // Apply incremental delta: remove levels with size == 0
        for (p, s) in bids {
            if *s == 0.0 {
                self.bids.retain(|(price, _)| *price != *p);
            } else if let Some(existing) = self.bids.iter_mut().find(|(price, _)| *price == *p) {
                existing.1 = *s;
            } else {
                self.bids.push((*p, *s));
            }
        }

        for (p, s) in asks {
            if *s == 0.0 {
                self.asks.retain(|(price, _)| *price != *p);
            } else if let Some(existing) = self.asks.iter_mut().find(|(price, _)| *price == *p) {
                existing.1 = *s;
            } else {
                self.asks.push((*p, *s));
            }
        }

        self.seq = seq;
        "delta"
    }

    pub fn best(&self) -> Option<(f64, f64)> {
        match (self.bids.first(), self.asks.first()) {
            (Some(b), Some(a)) => Some((b.0, a.0)),
            _ => None,
        }
    }
}

// Example usage:
// let mut book = OrderBook::new();
// let outcome = book.apply(&[(68863.5, 0.1)], &[(68864.0, 0.2)], 1);
// println!("{outcome}: best={:?}", book.best());

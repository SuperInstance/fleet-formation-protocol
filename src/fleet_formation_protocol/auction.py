"""Vickrey Auction — second-price sealed bid for agent allocation conflicts."""
from dataclasses import dataclass


@dataclass
class AuctionBid:
    formation_id: str
    agent_id: str  # the contested agent
    bid: float     # bid = trust_score + urgency bonus
    urgency: float  # 0.0-1.0, how badly this formation needs the agent


class VickreyAuction:
    """Second-price sealed bid auction.
    Winner pays the second-highest bid price.
    """

    def __init__(self):
        self._bids: list[AuctionBid] = []

    def submit_bid(self, formation_id: str, agent_id: str, bid: float, urgency: float = 0.0) -> None:
        self._bids.append(AuctionBid(
            formation_id=formation_id,
            agent_id=agent_id,
            bid=bid,
            urgency=urgency,
        ))

    def resolve(self) -> dict:
        """Resolve the auction. Returns winner and price paid (second price)."""
        if not self._bids:
            return {"winner": None, "price": 0.0, "bids": 0}

        # Sort by bid descending
        sorted_bids = sorted(self._bids, key=lambda b: b.bid, reverse=True)

        winner = sorted_bids[0]
        # Second price = highest losing bid, or winner's bid if only one bidder
        if len(sorted_bids) > 1:
            price = sorted_bids[1].bid
        else:
            price = winner.bid

        return {
            "winner_formation": winner.formation_id,
            "contested_agent": winner.agent_id,
            "price": price,
            "winning_bid": winner.bid,
            "urgency": winner.urgency,
            "total_bids": len(self._bids),
        }

    def clear(self) -> None:
        self._bids.clear()

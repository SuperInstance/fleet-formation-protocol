"""Formation Protocol — discover, negotiate, form, dissolve."""
import time
import uuid
from .types import FormationType, FormationState
from .agent import AgentProfile
from .formation import Formation
from .auction import VickreyAuction


class FormationProtocol:
    def __init__(self, timeout_seconds: int = 300):
        self._formations: dict[str, Formation] = {}
        self._timeout = timeout_seconds

    def discover(self, agents: list[AgentProfile],
                 required_capabilities: list[str] | None = None,
                 min_trust: float = 0.0) -> list[AgentProfile]:
        """Find compatible agents by capability and trust."""
        candidates = [a for a in agents if a.available and a.trust_score >= min_trust]
        if required_capabilities:
            candidates = [a for a in candidates if a.has_any_capability(required_capabilities)]
        return sorted(candidates, key=lambda a: a.trust_score, reverse=True)

    def negotiate(self, agents: list[AgentProfile],
                  formation_type: FormationType,
                  required_capabilities: list[str] | None = None) -> Formation:
        """Create a formation from available agents."""
        formation_id = str(uuid.uuid4())[:8]
        formation = Formation(
            formation_id=formation_id,
            formation_type=formation_type,
            timeout_seconds=self._timeout,
        )

        # Filter agents by capability if specified
        if required_capabilities:
            candidates = [a for a in agents if a.has_any_capability(required_capabilities) and a.available]
        else:
            candidates = [a for a in agents if a.available]

        # Sort by trust score (highest first)
        candidates.sort(key=lambda a: a.trust_score, reverse=True)

        for agent in candidates:
            if len(formation.agents) >= formation.max_size:
                break
            formation.add_agent(agent)

        self._formations[formation_id] = formation
        return formation

    def form(self, formation_id: str, agents: list[AgentProfile],
             formation_type: FormationType) -> Formation:
        """Create a formation with explicit ID and agents."""
        formation = Formation(
            formation_id=formation_id,
            formation_type=formation_type,
            agents=list(agents),
            timeout_seconds=self._timeout,
        )
        formation.activate()
        self._formations[formation_id] = formation
        return formation

    def dissolve(self, formation_id: str, reason: str = "") -> dict:
        """Dissolve a formation."""
        formation = self._formations.get(formation_id)
        if not formation:
            return {"error": "formation not found", "formation_id": formation_id}
        return formation.dissolve(reason)

    def heartbeat(self, formation_id: str) -> dict:
        """Check formation health. Auto-dissolve if timed out."""
        formation = self._formations.get(formation_id)
        if not formation:
            return {"error": "formation not found"}

        if formation.is_timed_out and formation.state == FormationState.ACTIVE:
            formation.dissolve("timeout")
            return {"formation_id": formation_id, "state": "DISSOLVED", "reason": "timeout"}

        return {
            "formation_id": formation_id,
            "state": formation.state.name,
            "agents": len(formation.agents),
            "is_valid": formation.is_valid_size,
            "age_seconds": time.time() - formation.created_at,
        }

    def resolve_conflict(self, formation_a: str, formation_b: str,
                         contested_agent_id: str) -> dict:
        """Two formations want the same agent. Vickrey auction."""
        fa = self._formations.get(formation_a)
        fb = self._formations.get(formation_b)
        if not fa or not fb:
            return {"error": "formation not found"}

        auction = VickreyAuction()
        # Bid = trust score of formation leader * urgency (agents needed / max)
        urgency_a = 1.0 - (len(fa.agents) / fa.max_size)
        urgency_b = 1.0 - (len(fb.agents) / fb.max_size)

        bid_a = (fa.leader.trust_score if fa.leader else 0.5) + urgency_a
        bid_b = (fb.leader.trust_score if fb.leader else 0.5) + urgency_b

        auction.submit_bid(formation_a, contested_agent_id, bid_a, urgency_a)
        auction.submit_bid(formation_b, contested_agent_id, bid_b, urgency_b)

        return auction.resolve()

    def list_formations(self) -> list[dict]:
        """List all formations."""
        return [f.to_dict() for f in self._formations.values()]

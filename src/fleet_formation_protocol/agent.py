"""Agent profile for fleet formation."""
from dataclasses import dataclass, field


@dataclass
class AgentProfile:
    agent_id: str
    capabilities: list[str] = field(default_factory=list)
    trust_score: float = 0.5
    latency_ms: int = 100
    available: bool = True

    def has_capability(self, cap: str) -> bool:
        return cap.lower() in [c.lower() for c in self.capabilities]

    def has_any_capability(self, caps: list[str]) -> bool:
        return any(self.has_capability(c) for c in caps)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "trust_score": self.trust_score,
            "latency_ms": self.latency_ms,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AgentProfile":
        return cls(
            agent_id=d["agent_id"],
            capabilities=d.get("capabilities", []),
            trust_score=d.get("trust_score", 0.5),
            latency_ms=d.get("latency_ms", 100),
            available=d.get("available", True),
        )

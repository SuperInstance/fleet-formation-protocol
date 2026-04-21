"""Formation — a group of agents organized for a task."""
import time
from dataclasses import dataclass, field
from .types import FormationType, FormationState, FORMATION_SIZE_LIMITS
from .agent import AgentProfile


@dataclass
class Formation:
    formation_id: str
    formation_type: FormationType
    agents: list[AgentProfile] = field(default_factory=list)
    state: FormationState = FormationState.FORMING
    created_at: float = field(default_factory=time.time)
    timeout_seconds: int = 300

    @property
    def leader(self) -> AgentProfile | None:
        if not self.agents:
            return None
        return max(self.agents, key=lambda a: a.trust_score)

    @property
    def min_size(self) -> int:
        return FORMATION_SIZE_LIMITS[self.formation_type][0]

    @property
    def max_size(self) -> int:
        return FORMATION_SIZE_LIMITS[self.formation_type][1]

    @property
    def is_valid_size(self) -> bool:
        return self.min_size <= len(self.agents) <= self.max_size

    @property
    def is_timed_out(self) -> bool:
        return time.time() - self.created_at > self.timeout_seconds

    def add_agent(self, agent: AgentProfile) -> bool:
        if len(self.agents) >= self.max_size:
            return False
        if not agent.available:
            return False
        self.agents.append(agent)
        return True

    def remove_agent(self, agent_id: str) -> bool:
        for i, a in enumerate(self.agents):
            if a.agent_id == agent_id:
                self.agents.pop(i)
                return True
        return False

    def activate(self) -> bool:
        if self.is_valid_size and self.state == FormationState.FORMING:
            self.state = FormationState.ACTIVE
            return True
        return False

    def dissolve(self, reason: str = "") -> dict:
        self.state = FormationState.DISSOLVED
        return {
            "formation_id": self.formation_id,
            "state": self.state.name,
            "reason": reason,
            "agent_count": len(self.agents),
            "duration": time.time() - self.created_at,
        }

    def to_dict(self) -> dict:
        return {
            "formation_id": self.formation_id,
            "formation_type": self.formation_type.name,
            "state": self.state.name,
            "agents": [a.to_dict() for a in self.agents],
            "leader": self.leader.to_dict() if self.leader else None,
            "created_at": self.created_at,
            "is_valid_size": self.is_valid_size,
        }

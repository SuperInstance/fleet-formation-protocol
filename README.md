# Fleet Formation Protocol

Self-organizing agent groups for the Cocapn fleet.

## Install

```bash
pip install fleet-formation-protocol
```

## Usage

```python
from fleet_formation_protocol import (
    FormationProtocol, FormationType, AgentProfile,
    FormationMessage, VickreyAuction,
)

# Create agents
agents = [
    AgentProfile("scout-1", capabilities=["navigation", "sensing"], trust_score=0.8),
    AgentProfile("worker-1", capabilities=["execution", "building"], trust_score=0.7),
    AgentProfile("scout-2", capabilities=["navigation"], trust_score=0.6),
]

# Form a scout party
protocol = FormationProtocol()
formation = protocol.negotiate(agents, FormationType.SCOUT_PARTY, required_capabilities=["navigation"])
print(f"Formation {formation.formation_id}: {len(formation.agents)} agents, leader: {formation.leader.agent_id}")

# Send a formation message (binary format, max 1024 bytes)
msg = FormationMessage(
    msg_type=3,  # FORM
    formation_id=1,
    agent_id=42,
    formation_type=FormationType.WORK_CREW,
    payload={"task": "explore sector 7"},
)
data = msg.serialize()  # → bytes
restored = FormationMessage.deserialize(data)  # → FormationMessage

# Resolve conflicts (Vickrey auction)
result = protocol.resolve_conflict("formation_a", "formation_b", "contested_agent")
print(f"Winner: {result['winner_formation']}, price: {result['price']}")
```

## Formation Types

| Type | Size | Purpose |
|------|------|---------|
| SCOUT_PARTY | 2-4 | Exploration |
| WORK_CREW | 3-8 | Task execution |
| WAR_ROOM | 4-6 | Strategic planning |
| RELAY_CHAIN | 2-10 | Communication |
| COUNCIL | 5-12 | Governance |

## Binary Message Format

16-byte header + JSON payload (max 1024 bytes total):

```
| version (1B) | type (1B) | formation_id (4B) | agent_id (4B) | formation_type (1B) | payload_len (2B) | checksum (3B) |
```

CRC-24 checksum over payload. Zero dependencies.

## License

MIT

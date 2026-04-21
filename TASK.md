# Fleet Formation Protocol — Implementation Task

Build a pip-installable Python package `fleet-formation-protocol` (v0.1.0).

## Package Structure
```
fleet_formation_protocol/
    __init__.py       — exports key classes
    formation.py      — Formation, FormationType, FormationState
    agent.py          — AgentProfile (capabilities, trust score, latency)
    protocol.py       — FormationProtocol (discover, negotiate, form, dissolve)
    message.py        — FormationMessage (binary format, serialize/deserialize)
    auction.py        — VickreyAuction for agent allocation conflicts
types.py             — Type aliases and enums
```

## Core Spec

### FormationType (enum)
- SCOUT_PARTY (2-4 agents, exploration)
- WORK_CREW (3-8 agents, task execution)
- WAR_ROOM (4-6 agents, strategic planning)
- RELAY_CHAIN (2-10 agents, communication)
- COUNCIL (5-12 agents, governance/decisions)

### AgentProfile
- agent_id: str
- capabilities: list[str]
- trust_score: float (0.0-1.0)
- latency_ms: int
- available: bool

### FormationMessage (binary format)
Header (16 bytes):
- version: 1 byte (0x01)
- msg_type: 1 byte (DISCOVER=1, NEGOTIATE=2, FORM=3, DISSOLVE=4, HEARTBEAT=5)
- formation_id: 4 bytes (uint32)
- agent_id: 4 bytes (uint32)
- formation_type: 1 byte
- payload_length: 2 bytes (uint16)
- checksum: 3 bytes (CRC-24)

Payload: JSON-encoded dict (variable length, max 1008 bytes)
Total max: 1024 bytes

### FormationProtocol
Methods:
- discover(agents: list[AgentProfile]) -> list[AgentProfile]  — find compatible agents
- negotiate(agents: list[AgentProfile], formation_type: FormationType) -> Formation  — create formation
- form(formation_id: str, agents: list[AgentProfile], formation_type: FormationType) -> Formation
- dissolve(formation_id: str, reason: str) -> dict
- heartbeat(formation_id: str) -> FormationState

### VickreyAuction
- Two formations want the same agent. Each bids (trust_score + urgency). Second-price auction.
- resolve(conflict: dict) -> dict  — returns winner and price

### Formation
- formation_id: str
- formation_type: FormationType
- agents: list[AgentProfile]
- leader: AgentProfile (highest trust)
- state: FormationState (FORMING, ACTIVE, DISSOLVING, DISSOLVED)
- created_at: float (timestamp)
- max_size: int (depends on formation type)
- timeout_seconds: int (default 300)

### Tests (pytest)
- test_message_serialization — round-trip binary serialize/deserialize
- test_formation_create — create a WORK_CREW formation
- test_formation_dissolve — create then dissolve
- test_discovery_filter — discover filters by capability match
- test_vickrey_auction — two formations bid for one agent, second-price wins
- test_formation_size_limits — SCOUT_PARTY max 4, COUNCIL max 12
- test_heartbeat_timeout — formation auto-dissolves after timeout

### pyproject.toml
- name: fleet-formation-protocol
- version: 0.1.0
- zero dependencies
- requires-python >= 3.8
- MIT license

### README.md
Short README explaining FFP, usage example, installation.

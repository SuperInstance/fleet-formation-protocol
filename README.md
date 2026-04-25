# fleet-formation-protocol

Self-organizing agent groups for the Cocapn fleet.

Agents don't wait for orders — they self-organize into formations based on task requirements. Like a school of fish that forms shapes without a leader.

## Formation Types

- **Line** — Sequential pipeline (agent A → B → C)
- **Ring** — Circular processing with consensus
- **Star** — One coordinator, many workers
- **Mesh** — Fully connected, emergent coordination

## What It Does

- **Agent Registration** — Agents declare capabilities and availability
- **Auction** — Tasks are auctioned to capable agents
- **Formation** — Winning agents self-organize into the right shape
- **Messaging** — Structured communication within the formation
- **Dissolution** — Clean teardown when the task completes

## Installation

```bash
pip install fleet-formation-protocol
```

## Part of the Cocapn Fleet

Used when multiple agents need to collaborate on a single task.

## License

MIT

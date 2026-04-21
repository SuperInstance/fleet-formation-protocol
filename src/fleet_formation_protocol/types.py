"""Type definitions for Fleet Formation Protocol."""
from enum import IntEnum


class FormationType(IntEnum):
    SCOUT_PARTY = 1   # 2-4 agents, exploration
    WORK_CREW = 2     # 3-8 agents, task execution
    WAR_ROOM = 3      # 4-6 agents, strategic planning
    RELAY_CHAIN = 4   # 2-10 agents, communication
    COUNCIL = 5       # 5-12 agents, governance


class FormationState(IntEnum):
    FORMING = 1
    ACTIVE = 2
    DISSOLVING = 3
    DISSOLVED = 4


class MessageType(IntEnum):
    DISCOVER = 1
    NEGOTIATE = 2
    FORM = 3
    DISSOLVE = 4
    HEARTBEAT = 5


FORMATION_SIZE_LIMITS = {
    FormationType.SCOUT_PARTY: (2, 4),
    FormationType.WORK_CREW: (3, 8),
    FormationType.WAR_ROOM: (4, 6),
    FormationType.RELAY_CHAIN: (2, 10),
    FormationType.COUNCIL: (5, 12),
}

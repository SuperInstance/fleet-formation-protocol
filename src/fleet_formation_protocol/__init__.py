"""Fleet Formation Protocol — self-organizing agent groups."""
from .types import FormationType, FormationState
from .agent import AgentProfile
from .formation import Formation
from .message import FormationMessage
from .auction import VickreyAuction
from .protocol import FormationProtocol

__version__ = "0.1.0"
__all__ = [
    "FormationType", "FormationState", "AgentProfile", "Formation",
    "FormationMessage", "VickreyAuction", "FormationProtocol",
]

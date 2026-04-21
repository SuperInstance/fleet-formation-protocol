"""Tests for Fleet Formation Protocol."""
import time
import pytest
from fleet_formation_protocol import (
    FormationType, FormationState, AgentProfile, Formation,
    FormationMessage, VickreyAuction, FormationProtocol,
)
from fleet_formation_protocol.message import MessageType


def make_agent(aid: str, caps: list[str] = None, trust: float = 0.5) -> AgentProfile:
    return AgentProfile(agent_id=aid, capabilities=caps or ["general"], trust_score=trust)


# --- Message Serialization ---

class TestMessageSerialization:
    def test_round_trip(self):
        msg = FormationMessage(
            msg_type=MessageType.DISCOVER,
            formation_id=42,
            agent_id=7,
            formation_type=FormationType.WORK_CREW,
            payload={"capabilities": ["navigation", "sensing"]},
        )
        data = msg.serialize()
        assert len(data) <= 1024
        restored = FormationMessage.deserialize(data)
        assert restored.version == 1
        assert restored.msg_type == MessageType.DISCOVER
        assert restored.formation_id == 42
        assert restored.agent_id == 7
        assert restored.formation_type == FormationType.WORK_CREW
        assert restored.payload["capabilities"] == ["navigation", "sensing"]

    def test_max_size(self):
        big_payload = {"data": "x" * 900}
        msg = FormationMessage(payload=big_payload)
        data = msg.serialize()
        assert len(data) <= 1024

    def test_checksum_tamper_detection(self):
        msg = FormationMessage(payload={"test": True})
        data = bytearray(msg.serialize())
        data[20] ^= 0xFF  # corrupt payload
        with pytest.raises(ValueError, match="Checksum"):
            FormationMessage.deserialize(bytes(data))


# --- Formation ---

class TestFormation:
    def test_create_work_crew(self):
        agents = [make_agent(f"a{i}", trust=0.5 + i*0.1) for i in range(5)]
        fp = FormationProtocol()
        f = fp.negotiate(agents, FormationType.WORK_CREW)
        assert f.formation_type == FormationType.WORK_CREW
        assert len(f.agents) >= 3
        assert f.state == FormationState.FORMING

    def test_dissolve(self):
        agents = [make_agent(f"a{i}") for i in range(4)]
        fp = FormationProtocol()
        f = fp.form("test-1", agents, FormationType.SCOUT_PARTY)
        result = fp.dissolve("test-1", "task complete")
        assert result["state"] == "DISSOLVED"
        assert result["reason"] == "task complete"

    def test_leader_highest_trust(self):
        agents = [make_agent("low", trust=0.2), make_agent("high", trust=0.9), make_agent("mid", trust=0.5)]
        fp = FormationProtocol()
        f = fp.form("test-2", agents, FormationType.SCOUT_PARTY)
        assert f.leader.agent_id == "high"


# --- Discovery ---

class TestDiscovery:
    def test_filter_by_capability(self):
        agents = [
            make_agent("nav", ["navigation"]),
            make_agent("sense", ["sensing"]),
            make_agent("both", ["navigation", "sensing"]),
            make_agent("none", ["cooking"]),
        ]
        fp = FormationProtocol()
        found = fp.discover(agents, required_capabilities=["navigation"])
        ids = [a.agent_id for a in found]
        assert "nav" in ids
        assert "both" in ids
        assert "sense" not in ids
        assert "none" not in ids

    def test_filter_by_trust(self):
        agents = [make_agent(f"a{i}", trust=i*0.3) for i in range(5)]
        fp = FormationProtocol()
        found = fp.discover(agents, min_trust=0.5)
        assert all(a.trust_score >= 0.5 for a in found)


# --- Vickrey Auction ---

class TestVickreyAuction:
    def test_second_price_wins(self):
        auction = VickreyAuction()
        auction.submit_bid("formation_a", "agent_x", bid=0.9, urgency=0.3)
        auction.submit_bid("formation_b", "agent_x", bid=0.7, urgency=0.2)
        result = auction.resolve()
        assert result["winner_formation"] == "formation_a"
        assert result["price"] == 0.7  # second price
        assert result["winning_bid"] == 0.9

    def test_single_bidder(self):
        auction = VickreyAuction()
        auction.submit_bid("only", "agent_y", bid=0.8)
        result = auction.resolve()
        assert result["winner_formation"] == "only"
        assert result["price"] == 0.8  # pays own bid

    def test_no_bids(self):
        auction = VickreyAuction()
        result = auction.resolve()
        assert result["winner"] is None


# --- Size Limits ---

class TestSizeLimits:
    def test_scout_party_max_4(self):
        agents = [make_agent(f"a{i}") for i in range(10)]
        fp = FormationProtocol()
        f = fp.negotiate(agents, FormationType.SCOUT_PARTY)
        assert len(f.agents) <= 4

    def test_council_max_12(self):
        agents = [make_agent(f"a{i}") for i in range(20)]
        fp = FormationProtocol()
        f = fp.negotiate(agents, FormationType.COUNCIL)
        assert len(f.agents) <= 12

    def test_scout_party_min(self):
        f = Formation(formation_id="test", formation_type=FormationType.SCOUT_PARTY)
        assert f.min_size == 2
        assert f.max_size == 4


# --- Timeout ---

class TestTimeout:
    def test_auto_dissolve_on_timeout(self):
        agents = [make_agent(f"a{i}") for i in range(3)]
        fp = FormationProtocol(timeout_seconds=0)  # instant timeout
        f = fp.form("timeout-test", agents, FormationType.SCOUT_PARTY)
        f.created_at = time.time() - 1  # force timeout
        result = fp.heartbeat("timeout-test")
        assert result["state"] == "DISSOLVED"
        assert result["reason"] == "timeout"

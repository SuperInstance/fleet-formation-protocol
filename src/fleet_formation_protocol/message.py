"""Formation Message — binary format with 16-byte header."""
import json
import struct
import zlib
from dataclasses import dataclass
from .types import MessageType, FormationType

HEADER_FORMAT = "!BBII B H 3s"  # 16 bytes total
HEADER_SIZE = 16
MAX_PAYLOAD = 1008  # 1024 - 16


@dataclass
class FormationMessage:
    version: int = 1
    msg_type: MessageType = MessageType.DISCOVER
    formation_id: int = 0
    agent_id: int = 0
    formation_type: FormationType = FormationType.SCOUT_PARTY
    payload: dict = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}

    def serialize(self) -> bytes:
        """Serialize to binary format (max 1024 bytes)."""
        payload_bytes = json.dumps(self.payload).encode("utf-8")
        if len(payload_bytes) > MAX_PAYLOAD:
            raise ValueError(f"Payload too large: {len(payload_bytes)} > {MAX_PAYLOAD}")

        # CRC-24 of payload
        crc = zlib.crc32(payload_bytes) & 0xFFFFFF
        checksum = crc.to_bytes(3, "big")

        header = struct.pack(
            HEADER_FORMAT,
            self.version,
            self.msg_type,
            self.formation_id,
            self.agent_id,
            self.formation_type,
            len(payload_bytes),
            checksum,
        )
        return header + payload_bytes

    @classmethod
    def deserialize(cls, data: bytes) -> "FormationMessage":
        """Deserialize from binary format."""
        if len(data) < HEADER_SIZE:
            raise ValueError(f"Data too short: {len(data)} < {HEADER_SIZE}")

        version, msg_type, formation_id, agent_id, formation_type, payload_len, checksum = \
            struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])

        payload_bytes = data[HEADER_SIZE:HEADER_SIZE + payload_len]
        if len(payload_bytes) != payload_len:
            raise ValueError(f"Payload length mismatch: {len(payload_bytes)} != {payload_len}")

        # Verify checksum
        crc = zlib.crc32(payload_bytes) & 0xFFFFFF
        expected = int.from_bytes(checksum, "big")
        if crc != expected:
            raise ValueError(f"Checksum mismatch: {crc:#x} != {expected:#x}")

        payload = json.loads(payload_bytes.decode("utf-8"))

        return cls(
            version=version,
            msg_type=MessageType(msg_type),
            formation_id=formation_id,
            agent_id=agent_id,
            formation_type=FormationType(formation_type),
            payload=payload,
        )

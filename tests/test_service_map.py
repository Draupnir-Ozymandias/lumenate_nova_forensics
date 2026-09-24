import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_MAP = ROOT / "protocol_reconstruction/lumenate_nova/service-map.json"


def load_service_map() -> dict:
    return json.loads(SERVICE_MAP.read_text(encoding="utf-8"))


def test_service_map_identity_and_unique_uuids() -> None:
    document = load_service_map()

    assert document["format"] == "lumenate-nova-service-map"
    assert document["format_version"] == "1.0.0"
    assert document["reviewed_app_version"] == "7.2.1"
    assert document["reviewed_device_firmware"] == "1.0.4"

    service_uuids = [service["uuid"] for service in document["services"]]
    characteristic_uuids = [
        characteristic["uuid"]
        for service in document["services"]
        for characteristic in service["characteristics"]
    ]

    assert len(service_uuids) == len(set(service_uuids))
    assert len(characteristic_uuids) == len(set(characteristic_uuids))


def test_service_map_preserves_the_bounded_unknown() -> None:
    document = load_service_map()
    characteristics = {
        characteristic["uuid"]: characteristic
        for service in document["services"]
        for characteristic in service["characteristics"]
    }

    unknown = characteristics["2b35ef1f-11a6-4089-8cd5-843c5d0c9c55"]
    assert unknown["role"] is None
    assert unknown["status"] == "firmware_exposed_current_app_unused"

    offline_state = characteristics["2a84aaff-6738-4629-894c-346357b89a0c"]
    assert offline_state["values"]["01"] == "explore"
    assert offline_state["observed_value_hex"] == "01"

    offline_header = characteristics["51bfc219-feab-4227-8b93-8af8cc5306d4"]
    assert offline_header["observed_header_prefix_hex"] == (
        "4e4c464f010000000000000001000000"
    )


def test_service_map_evidence_hashes_are_sha256() -> None:
    document = load_service_map()
    hashes = {
        key: value
        for key, value in document["evidence"].items()
        if key.endswith("_sha256")
    }

    assert hashes
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes.values())

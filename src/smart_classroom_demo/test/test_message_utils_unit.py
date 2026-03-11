from smart_classroom_demo.message_utils import (
    build_payload,
    parse_csv_field,
    parse_payload,
)


def test_build_payload_serializes_list_fields_as_csv():
    payload = build_payload(
        round=2, signed_students=["张三", "李四"], state="running"
    )

    parsed = parse_payload(payload)

    assert parsed["round"] == "2"
    assert parsed["state"] == "running"
    assert parsed["signed_students"] == "张三,李四"


def test_parse_csv_field_handles_empty_marker():
    assert parse_csv_field("-") == []
    assert parse_csv_field("") == []


def test_parse_csv_field_returns_items_in_order():
    assert parse_csv_field("张三, 李四, 王五") == ["张三", "李四", "王五"]

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import CATEGORIES, assert_catalog
from study import (
    CSV_FIELDS,
    StudyError,
    bootstrap_label_effect,
    build_round,
    checkout_result,
    label_order,
    observation_row,
    parse_cognitive_state,
    public_round,
    rows_to_csv,
    sequence_for_count,
    session_payload,
    sponsored_for_round,
)


def test_catalog_rules_hold():
    assert_catalog()
    assert len(CATEGORIES) == 10


def test_counterbalance_flips_the_label_and_keeps_five_each():
    order_a = [sponsored_for_round("A", n) for n in range(1, 11)]
    order_b = [sponsored_for_round("B", n) for n in range(1, 11)]
    assert order_a.count(True) == 5
    assert order_b.count(True) == 5
    assert order_b == [not flag for flag in order_a]
    assert label_order("A") == "SUSUSUSUSU"
    assert label_order("B") == "USUSUSUSUS"
    assert [sequence_for_count(n) for n in range(1, 7)] == ["A", "B", "A", "B", "A", "B"]


def test_target_stays_top_left_and_label_does_not_leak():
    labeled = build_round(CATEGORIES[0], 1, True, random.Random(1))
    unlabeled = build_round(CATEGORIES[3], 2, False, random.Random(2))
    assert labeled["products"][0]["id"] == labeled["target_id"]
    assert unlabeled["products"][0]["id"] == unlabeled["target_id"]

    public_labeled = public_round(labeled)
    public_plain = public_round(unlabeled)
    assert "target_id" not in public_labeled
    assert "sponsored_label" not in public_labeled
    assert public_labeled["products"][0]["sponsored"] is True
    assert all(not product["sponsored"] for product in public_labeled["products"][1:])
    assert all(not product["sponsored"] for product in public_plain["products"])
    neighbor_ids = [product["id"] for product in labeled["products"][1:]]
    assert labeled["target_id"] not in neighbor_ids


def test_shopper_payload_hides_the_assignment():
    aisle = build_round(CATEGORIES[0], 1, True, random.Random(1))
    payload = session_payload({
        "_id": "abc",
        "participant_code": "",
        "current_round": 1,
        "completed": False,
        "rounds": [aisle],
    })
    assert "sequence" not in payload
    assert "label_order" not in payload
    assert "cognitive_state" not in payload
    assert payload["round"]["products"][0]["id"] == aisle["target_id"]
    assert "target" not in payload["round"]["products"][0]


def test_checkout_records_click_and_purchase_share_fields():
    aisle = build_round(CATEGORIES[0], 1, True, random.Random(0))
    target = aisle["target_id"]
    cheap = min(
        (product for product in aisle["products"] if product["id"] != target),
        key=lambda product: product["price"],
    )
    bought = checkout_result(aisle, [], [target])
    assert bought["clicked_target"] == 1
    assert bought["purchased_target"] == 1
    assert bought["target_spend"] == aisle["products"][0]["price"]

    looked = checkout_result(aisle, [target], [cheap["id"]])
    assert looked["clicked_target"] == 1
    assert looked["purchased_target"] == 0
    assert looked["target_spend"] == 0
    assert looked["spend"] == cheap["price"]


def test_checkout_rejects_empty_unknown_and_over_budget():
    aisle = build_round(CATEGORIES[4], 5, False, random.Random(4))
    ids = [product["id"] for product in aisle["products"]]
    with pytest.raises(StudyError, match="at least one"):
        checkout_result(aisle, [], [])
    with pytest.raises(StudyError, match="not in this aisle"):
        checkout_result(aisle, [], ["not-a-product"])
    with pytest.raises(StudyError, match="over the aisle budget"):
        checkout_result(aisle, ids, ids)


def test_cognitive_state_rejects_bools_and_out_of_range():
    assert parse_cognitive_state(4) == 4
    with pytest.raises(StudyError):
        parse_cognitive_state(True)
    with pytest.raises(StudyError):
        parse_cognitive_state(0)
    with pytest.raises(StudyError):
        parse_cognitive_state(8)


def test_csv_matches_the_regression_columns():
    aisle = build_round(CATEGORIES[1], 1, True, random.Random(3))
    result = checkout_result(aisle, [aisle["target_id"]], [aisle["target_id"]])
    observation = {
        "participant_id": "person-1",
        "participant_code": "Section A, seat 2",
        "sequence": "A",
        "cognitive_state": 5,
        "round_num": 1,
        "category": aisle["category"],
        "budget": aisle["budget"],
        "sponsored_label": 1,
        "price": result["target_price"],
        "clicked_target": result["clicked_target"],
        "purchased_target": result["purchased_target"],
        "spend": result["spend"],
        "target_spend": result["target_spend"],
        "n_items": result["n_items"],
        "duration_ms": 1200,
        "target_name": result["target_name"],
        "purchased_items": result["purchased_items"],
        "clicked_ids": result["clicked_ids"],
        "click_log": [{"id": aisle["target_id"], "at_ms": 400}],
        "created_at": "2026-10-05T00:00:00+00:00",
    }
    row = observation_row(observation, {"completed": True})
    text = rows_to_csv([row])
    header = text.splitlines()[0].split(",")
    for field in ("purchased_target", "sponsored_label", "price", "round_num", "cognitive_state", "participant_id"):
        assert field in header
    assert header == CSV_FIELDS
    assert "Section A, seat 2" in text
    assert row["first_click_id"] == aisle["target_id"]


def test_bootstrap_resamples_people_and_keeps_direction():
    rows = []
    for person in range(8):
        for round_num, label in enumerate([1, 0, 1, 0], start=1):
            rows.append({
                "participant_id": f"p{person}",
                "sponsored_label": label,
                "purchased_target": label,
                "clicked_target": label,
                "spend": 10 if label else 4,
            })
    result = bootstrap_label_effect(rows, "purchased_target", n_boot=300, seed=1)
    assert result["estimate"] == 1
    assert result["ci_low"] > 0.9
    assert result["resamples"] == "participants"
    assert bootstrap_label_effect(rows[:1], "purchased_target") is None

"""Assignment, checkout checks, and the participant-level summary.

Position stays fixed: the target product is always products[0]. Half the
aisles carry a Sponsored label. Sequence A labels odd aisles and sequence B
labels even aisles, so the label order is counterbalanced across people.
"""

import csv
import io
import random

from catalog import CATEGORIES

TOTAL_ROUNDS = len(CATEGORIES)

CSV_FIELDS = [
    "participant_id",
    "participant_code",
    "sequence",
    "cognitive_state",
    "participant_completed",
    "round_num",
    "category",
    "budget",
    "sponsored_label",
    "price",
    "clicked_target",
    "purchased_target",
    "spend",
    "target_spend",
    "n_items",
    "duration_ms",
    "target_name",
    "purchased_names",
    "clicked_ids",
    "first_click_id",
]


class StudyError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def sequence_for_count(n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise StudyError("Participant counter is invalid.")
    return "A" if n % 2 else "B"


def sponsored_for_round(sequence, round_num):
    if sequence not in ("A", "B"):
        raise StudyError("Unknown label sequence.")
    if isinstance(round_num, bool) or not isinstance(round_num, int):
        raise StudyError("Unknown aisle.")
    if not 1 <= round_num <= TOTAL_ROUNDS:
        raise StudyError("Unknown aisle.")
    return (round_num % 2 == 1) if sequence == "A" else (round_num % 2 == 0)


def label_order(sequence):
    marks = []
    for round_num in range(1, TOTAL_ROUNDS + 1):
        marks.append("S" if sponsored_for_round(sequence, round_num) else "U")
    return "".join(marks)


def _clean_product(product):
    return {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "unit": product["unit"],
        "detail": product["detail"],
        "image": f"/products/{product['id']}.jpg?v=8",
    }


def build_round(category, round_num, sponsored, rng):
    products = [dict(product) for product in category["products"]]
    target = next(product for product in products if product.get("target"))
    others = [product for product in products if not product.get("target")]
    rng.shuffle(others)
    ordered = [target, *others]
    if ordered[0]["id"] != target["id"]:
        raise StudyError("The target product left the top-left slot.", 500)
    return {
        "round_num": round_num,
        "category": category["key"],
        "title": category["title"],
        "blurb": category["blurb"],
        "budget": category["budget"],
        "accent": category["accent"],
        "target_id": target["id"],
        "sponsored_label": bool(sponsored),
        "products": [_clean_product(product) for product in ordered],
    }


def build_rounds(sequence, rng):
    rounds = []
    for index, category in enumerate(CATEGORIES, start=1):
        rounds.append(build_round(category, index, sponsored_for_round(sequence, index), rng))
    return rounds


def public_round(round_doc):
    """Shopper payload. The target stays first, but it is not flagged as the target."""
    products = []
    for index, product in enumerate(round_doc["products"]):
        products.append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "unit": product["unit"],
            "detail": product["detail"],
            "image": f"/products/{product['id']}.jpg?v=8",
            "sponsored": bool(round_doc["sponsored_label"] and index == 0),
        })
    return {
        "round_num": round_doc["round_num"],
        "total_rounds": TOTAL_ROUNDS,
        "title": round_doc["title"],
        "blurb": round_doc["blurb"],
        "budget": round_doc["budget"],
        "accent": round_doc["accent"],
        "products": products,
    }


def parse_cognitive_state(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 7:
        raise StudyError("Choose a focus rating from 1 to 7.")
    return value


def parse_participant_code(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise StudyError("Participant code must be text.")
    return value.strip()[:64]


def parse_duration(value):
    # A bad timer should not throw away a finished aisle.
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if not isinstance(value, int) or value < 0 or value > 4 * 60 * 60 * 1000:
        return None
    return value


def parse_click_log(value, valid_ids):
    if value is None:
        return []
    if not isinstance(value, list):
        raise StudyError("Click log is invalid.")
    cleaned = []
    for entry in value[:80]:
        if not isinstance(entry, dict):
            continue
        product_id = entry.get("id")
        at_ms = entry.get("at_ms")
        if product_id not in valid_ids:
            continue
        if isinstance(at_ms, bool):
            continue
        if isinstance(at_ms, float) and at_ms.is_integer():
            at_ms = int(at_ms)
        if not isinstance(at_ms, int) or at_ms < 0:
            continue
        cleaned.append({"id": product_id, "at_ms": at_ms})
    return cleaned


def _id_list(value, label):
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise StudyError(f"{label} must be a list of product ids.")
    return value


def checkout_result(round_doc, clicked_ids, purchased_ids):
    products = {product["id"]: product for product in round_doc["products"]}
    if not round_doc["products"] or round_doc["products"][0]["id"] != round_doc["target_id"]:
        raise StudyError("This aisle is misconfigured.", 500)

    clicked_ids = _id_list(clicked_ids, "Clicks")
    purchased_ids = _id_list(purchased_ids, "Cart")
    if len(clicked_ids) > 40 or len(purchased_ids) > len(products):
        raise StudyError("Too many products in this aisle.")
    if len(purchased_ids) != len(set(purchased_ids)):
        raise StudyError("That item is already in the cart.")
    if not purchased_ids:
        raise StudyError("Add at least one item before checking out.")
    unknown = [item for item in clicked_ids + purchased_ids if item not in products]
    if unknown:
        raise StudyError("One of those items is not in this aisle.")

    purchased = [products[item] for item in purchased_ids]
    spend_cents = sum(int(round(item["price"] * 100)) for item in purchased)
    budget_cents = int(round(round_doc["budget"] * 100))
    if spend_cents > budget_cents:
        raise StudyError("That cart is over the aisle budget.")

    target_id = round_doc["target_id"]
    clicked = list(dict.fromkeys([*clicked_ids, *purchased_ids]))
    purchased_target = target_id in purchased_ids
    target = products[target_id]
    return {
        "spend": spend_cents / 100,
        "clicked_target": int(target_id in clicked),
        "purchased_target": int(purchased_target),
        "target_spend": target["price"] if purchased_target else 0,
        "target_price": target["price"],
        "target_name": target["name"],
        "n_items": len(purchased_ids),
        "clicked_ids": clicked,
        "purchased_items": [
            {"id": item["id"], "name": item["name"], "price": item["price"]}
            for item in purchased
        ],
        "shown_ids": [item["id"] for item in round_doc["products"]],
    }


def session_payload(doc, observations=None):
    completed = bool(doc.get("completed"))
    current = doc["current_round"]
    payload = {
        "participant_id": doc["_id"],
        "participant_code": doc.get("participant_code") or "",
        "total_rounds": TOTAL_ROUNDS,
        "current_round": current,
        "completed": completed,
        "round": None if completed else public_round(doc["rounds"][current - 1]),
    }
    if completed and observations is not None:
        ordered = sorted(observations, key=lambda item: item["round_num"])
        payload["summary"] = {
            "rounds": len(ordered),
            "items": sum(item["n_items"] for item in ordered),
            "total_spend": round(sum(item["spend"] for item in ordered), 2),
        }
        payload["aisles"] = [
            {
                "round_num": item["round_num"],
                "title": item["title"],
                "spend": item["spend"],
                "budget": item["budget"],
                "items": [product["name"] for product in item["purchased_items"]],
            }
            for item in ordered
        ]
    return payload


def make_receipt(observation):
    return {
        "round_num": observation["round_num"],
        "title": observation["title"],
        "budget": observation["budget"],
        "spend": observation["spend"],
        "items": observation["purchased_items"],
    }


def observation_row(obs, participant):
    completed = bool(participant.get("completed")) if participant else False
    click_log = obs.get("click_log") or []
    first_click = click_log[0]["id"] if click_log else ""
    created = obs.get("created_at")
    created_at = created.isoformat() if hasattr(created, "isoformat") else (created or "")
    return {
        "participant_id": obs["participant_id"],
        "participant_code": obs.get("participant_code") or "",
        "sequence": obs.get("sequence") or "",
        "cognitive_state": obs.get("cognitive_state"),
        "participant_completed": int(completed),
        "round_num": obs["round_num"],
        "category": obs.get("category") or "",
        "budget": obs.get("budget"),
        "sponsored_label": int(bool(obs.get("sponsored_label"))),
        "price": obs.get("price"),
        "clicked_target": int(bool(obs.get("clicked_target"))),
        "purchased_target": int(bool(obs.get("purchased_target"))),
        "spend": obs.get("spend"),
        "target_spend": obs.get("target_spend"),
        "n_items": obs.get("n_items"),
        "duration_ms": obs.get("duration_ms"),
        "target_name": obs.get("target_name") or "",
        "purchased_names": "|".join(item["name"] for item in obs.get("purchased_items") or []),
        "clicked_ids": "|".join(obs.get("clicked_ids") or []),
        "first_click_id": first_click,
        "created_at": created_at,
    }


def rows_to_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def _mean(values):
    return sum(values) / len(values)


def condition_stats(rows, labeled):
    subset = [row for row in rows if bool(row["sponsored_label"]) is labeled]
    n = len(subset)
    if n == 0:
        return {
            "n": 0,
            "click_share": None,
            "purchase_share": None,
            "avg_spend": None,
            "avg_target_spend": None,
        }
    return {
        "n": n,
        "click_share": round(_mean([row["clicked_target"] for row in subset]), 4),
        "purchase_share": round(_mean([row["purchased_target"] for row in subset]), 4),
        "avg_spend": round(_mean([row["spend"] for row in subset]), 2),
        "avg_target_spend": round(_mean([row["target_spend"] for row in subset]), 2),
    }


def bootstrap_label_effect(rows, key, n_boot=2000, seed=7):
    """Percentile bootstrap of sponsored mean minus unlabeled mean.

    Participants are resampled with replacement. A person's rounds stay
    together, because aisles from the same shopper are not independent.
    """
    by_person = {}
    for row in rows:
        by_person.setdefault(row["participant_id"], []).append(row)
    people = list(by_person.values())
    if len(people) < 2:
        return None

    def difference(groups):
        sponsored = []
        unlabeled = []
        for group in groups:
            for row in group:
                bucket = sponsored if row["sponsored_label"] else unlabeled
                bucket.append(row[key])
        if not sponsored or not unlabeled:
            return None
        return _mean(sponsored) - _mean(unlabeled)

    point = difference(people)
    if point is None:
        return None
    rng = random.Random(seed)
    samples = []
    for _ in range(n_boot):
        draw = [people[rng.randrange(len(people))] for _ in people]
        value = difference(draw)
        if value is not None:
            samples.append(value)
    if not samples:
        return None
    samples.sort()

    def percentile(p):
        index = int(round((len(samples) - 1) * p))
        return samples[index]

    return {
        "estimate": round(point, 4),
        "ci_low": round(percentile(0.025), 4),
        "ci_high": round(percentile(0.975), 4),
        "n_participants": len(people),
        "n_boot": len(samples),
        "resamples": "participants",
    }


def summarize(rows, participants):
    completed = sum(1 for person in participants if person.get("completed"))
    sequences = {"A": 0, "B": 0}
    for person in participants:
        sequence = person.get("sequence")
        if sequence in sequences:
            sequences[sequence] += 1
    return {
        "participants_started": len(participants),
        "participants_completed": completed,
        "observations": len(rows),
        "sequence_counts": sequences,
        "conditions": {
            "sponsored": condition_stats(rows, True),
            "unlabeled": condition_stats(rows, False),
        },
        "bootstrap": {
            "clicked_target": bootstrap_label_effect(rows, "clicked_target"),
            "purchased_target": bootstrap_label_effect(rows, "purchased_target"),
            "spend": bootstrap_label_effect(rows, "spend"),
        },
    }

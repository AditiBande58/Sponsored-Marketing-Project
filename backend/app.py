"""Campus Cart API.

Shoppers get ten aisles. The server stores what they click and buy.
Researcher routes are behind RESEARCHER_KEY.
"""

import hmac
import os
import random
import sys
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

from study import (  # noqa: E402
    TOTAL_ROUNDS,
    StudyError,
    build_rounds,
    label_order,
    make_receipt,
    observation_row,
    parse_click_log,
    parse_cognitive_state,
    parse_duration,
    parse_participant_code,
    rows_to_csv,
    sequence_for_count,
    session_payload,
    summarize,
    checkout_result,
)
from catalog import CATEGORIES  # noqa: E402

app = Flask(__name__)
app.json.sort_keys = False
CORS(app, resources={r"/api/*": {"origins": "*"}})

DIST = ROOT.parent / "frontend" / "dist"
PUBLIC = ROOT.parent / "frontend" / "public"
_client = None
_indexes_ready = False


def researcher_key():
    return os.environ.get("RESEARCHER_KEY", "campus-cart")


def mongo_db():
    global _client, _indexes_ready
    if _client is None:
        _client = MongoClient(
            os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
            serverSelectionTimeoutMS=2500,
        )
    _client.admin.command("ping")
    database = _client[os.environ.get("MONGODB_DB", "sponsored_marketing")]
    if not _indexes_ready:
        database.observations.create_index(
            [("participant_id", 1), ("round_num", 1)],
            unique=True,
        )
        _indexes_ready = True
    return database


def db_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except StudyError as exc:
            return jsonify({"error": exc.message}), exc.status
        except PyMongoError:
            app.logger.exception("database error")
            return jsonify({"error": "Database is not running. Start MongoDB and try again."}), 503

    return wrapper


def load_participant(db, participant_id):
    try:
        parsed = str(uuid.UUID(participant_id))
    except (ValueError, AttributeError, TypeError):
        raise StudyError("That shopping session was not found.", 404)
    doc = db.participants.find_one({"_id": parsed})
    if not doc:
        raise StudyError("That shopping session was not found.", 404)
    return doc


def present(db, doc, receipt=None):
    observations = None
    if doc.get("completed"):
        observations = list(db.observations.find({"participant_id": doc["_id"]}))
    return {"session": session_payload(doc, observations), "receipt": receipt}


def require_researcher():
    sent = request.headers.get("X-Researcher-Key", "")
    expected = researcher_key()
    if len(sent) != len(expected) or not hmac.compare_digest(sent, expected):
        raise StudyError("Researcher key was not recognized.", 401)


def result_rows(db, completed_only):
    participants = list(db.participants.find())
    by_id = {person["_id"]: person for person in participants}
    if completed_only:
        allowed = {person_id for person_id, person in by_id.items() if person.get("completed")}
        observations = list(db.observations.find({"participant_id": {"$in": list(allowed)}}))
        participants = [person for person in participants if person.get("completed")]
    else:
        observations = list(db.observations.find())
    rows = [observation_row(obs, by_id.get(obs["participant_id"])) for obs in observations]
    rows.sort(key=lambda row: (row["created_at"], row["round_num"]))
    return participants, rows


@app.get("/api/health")
@db_call
def health():
    mongo_db()
    return jsonify({"ok": True, "rounds": TOTAL_ROUNDS})


@app.get("/api/aisles")
def aisles():
    return jsonify({
        "total_rounds": TOTAL_ROUNDS,
        "aisles": [{"title": category["title"], "blurb": category["blurb"]} for category in CATEGORIES],
    })


@app.post("/api/sessions")
@db_call
def create_session():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        body = {}
    code = parse_participant_code(body.get("participant_code"))
    cognitive_state = parse_cognitive_state(body.get("cognitive_state"))
    db = mongo_db()
    counter = db.counters.find_one_and_update(
        {"_id": "participants"},
        {"$inc": {"n": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    sequence = sequence_for_count(counter["n"])
    participant_id = str(uuid.uuid4())
    doc = {
        "_id": participant_id,
        "participant_code": code,
        "cognitive_state": cognitive_state,
        "sequence": sequence,
        "label_order": label_order(sequence),
        "created_at": datetime.now(timezone.utc),
        "completed": False,
        "current_round": 1,
        "rounds": build_rounds(sequence, random.Random()),
    }
    db.participants.insert_one(doc)
    return jsonify(present(db, doc))


@app.get("/api/sessions/<participant_id>")
@db_call
def get_session(participant_id):
    db = mongo_db()
    doc = load_participant(db, participant_id)
    return jsonify(present(db, doc))


@app.post("/api/sessions/<participant_id>/rounds/<int:round_num>")
@db_call
def complete_round(participant_id, round_num):
    if round_num < 1 or round_num > TOTAL_ROUNDS:
        raise StudyError("Unknown aisle.", 404)
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        body = {}
    clicked_ids = body.get("clicked_ids")
    purchased_ids = body.get("purchased_ids")
    if clicked_ids is None or purchased_ids is None:
        raise StudyError("Send the clicks and the cart.")
    duration_ms = parse_duration(body.get("duration_ms"))

    db = mongo_db()
    doc = load_participant(db, participant_id)
    already_saved = bool(doc.get("completed")) or round_num < doc["current_round"]
    if not already_saved and round_num != doc["current_round"]:
        raise StudyError("This aisle is out of order.", 409)

    if not already_saved:
        round_doc = doc["rounds"][round_num - 1]
        result = checkout_result(round_doc, clicked_ids, purchased_ids)
        valid_ids = {product["id"] for product in round_doc["products"]}
        click_log = parse_click_log(body.get("click_log"), valid_ids)
        observation = {
            "participant_id": doc["_id"],
            "participant_code": doc.get("participant_code") or "",
            "sequence": doc["sequence"],
            "cognitive_state": doc["cognitive_state"],
            "round_num": round_num,
            "category": round_doc["category"],
            "title": round_doc["title"],
            "budget": round_doc["budget"],
            "sponsored_label": int(bool(round_doc["sponsored_label"])),
            "target_id": round_doc["target_id"],
            "target_name": result["target_name"],
            "price": result["target_price"],
            "clicked_target": result["clicked_target"],
            "purchased_target": result["purchased_target"],
            "spend": result["spend"],
            "target_spend": result["target_spend"],
            "n_items": result["n_items"],
            "duration_ms": duration_ms,
            "clicked_ids": result["clicked_ids"],
            "click_log": click_log,
            "purchased_items": result["purchased_items"],
            "shown_ids": result["shown_ids"],
            "created_at": datetime.now(timezone.utc),
        }
        try:
            db.observations.insert_one(observation)
        except DuplicateKeyError:
            pass
        completed = round_num == TOTAL_ROUNDS
        update = {
            "current_round": round_num if completed else round_num + 1,
            "completed": completed,
        }
        if completed:
            update["completed_at"] = datetime.now(timezone.utc)
        db.participants.update_one(
            {"_id": doc["_id"], "current_round": round_num},
            {"$set": update},
        )
        doc = load_participant(db, participant_id)

    observation = db.observations.find_one({"participant_id": doc["_id"], "round_num": round_num})
    receipt = make_receipt(observation) if observation else None
    return jsonify(present(db, doc, receipt))


@app.get("/api/results")
@db_call
def results():
    require_researcher()
    completed_only = request.args.get("completed") == "1"
    db = mongo_db()
    participants, rows = result_rows(db, completed_only)
    payload = summarize(rows, participants)
    payload["completed_only"] = completed_only
    payload["rows"] = rows
    return jsonify(payload)


@app.get("/api/results.csv")
@db_call
def results_csv():
    require_researcher()
    completed_only = request.args.get("completed") == "1"
    db = mongo_db()
    _participants, rows = result_rows(db, completed_only)
    response = app.response_class(rows_to_csv(rows), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=campus-cart-results.csv"
    return response


@app.after_request
def no_store(response):
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def spa(path):
    if path == "api" or path.startswith("api/"):
        abort(404)
    if not DIST.exists():
        return jsonify({
            "ok": True,
            "message": "API is running. Start the shop with npm run dev in the frontend folder.",
        })
    if path:
        public_root = PUBLIC.resolve()
        public_file = (PUBLIC / path).resolve()
        if public_file.is_file() and public_file.is_relative_to(public_root):
            return send_from_directory(PUBLIC, path)
        built = DIST / path
        if built.is_file():
            return send_from_directory(DIST, path)
    return send_from_directory(DIST, "index.html")


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug)

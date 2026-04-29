import json
import random
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from engines.fsi_policy import should_trigger_fsi
from engines.learning_engine import LearningEngine
from engines.quest_engine import QuestEngine
from engines.sentence_engine import SentenceEngine


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_BANK_PATH = BASE_DIR / "data" / "sample_sentence_bank.json"
DEFAULT_PROGRESS_PATH = BASE_DIR / "data" / "user_progress.json"


def load_sentence_bank(bank_path):
    with open(bank_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_app(sentence_bank=None, bank_path=None, progress_path=None, fsi_rng=None):
    app = Flask(__name__)

    bank_data = sentence_bank or load_sentence_bank(bank_path or DEFAULT_BANK_PATH)
    learning_engine = LearningEngine(str(progress_path or DEFAULT_PROGRESS_PATH))
    sentence_engine = SentenceEngine(bank_data)
    quest_engine = QuestEngine(bank_data, learning_engine)

    app.config["sentence_engine"] = sentence_engine
    app.config["learning_engine"] = learning_engine
    app.config["quest_engine"] = quest_engine
    app.config["fsi_rng"] = fsi_rng or random.random

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "engines": "ready"})

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/api/quest", methods=["GET"])
    def get_quest():
        user_id = request.args.get("user_id", "default_user")
        level = request.args.get("level")
        scenario = request.args.get("scenario")
        adaptive = request.args.get("adaptive", "false").lower() == "true"
        quest_engine = app.config["quest_engine"]
        if adaptive:
            quest_items = quest_engine.build_adaptive_quest(
                user_id,
                level=level,
                scenario=scenario,
            )
        else:
            quest_items = quest_engine.build_quest(
                user_id,
                level=level,
                scenario=scenario,
            )
        return jsonify({"quest_items": quest_items})

    @app.route("/api/question", methods=["GET"])
    def get_question():
        sentence_id = request.args.get("sentence_id")
        task_type = request.args.get("task_type", "original")

        payload = app.config["sentence_engine"].get_question_payload(sentence_id, task_type=task_type)
        if not payload:
            return jsonify({"error": "Question not found"}), 404
        return jsonify(payload)

    @app.route("/api/report/skills", methods=["GET"])
    def get_skill_report():
        user_id = request.args.get("user_id", "default_user")
        skill_report = app.config["learning_engine"].get_skill_report(user_id)
        return jsonify({"skills": skill_report})

    @app.route("/api/answer", methods=["POST"])
    def submit_answer():
        data = request.get_json() or {}
        question_id = data.get("question_id")
        user_chunk_ids = data.get("user_chunk_ids", [])
        user_id = data.get("user_id", "default_user")
        hint_used = bool(data.get("hint_used", False))

        sentence_engine = app.config["sentence_engine"]
        learning_engine = app.config["learning_engine"]
        result = sentence_engine.check_answer(question_id, user_chunk_ids)

        if result["mistake_type"] == "invalid_question_id":
            return jsonify(result), 400

        result["result_type"] = (
            "incorrect" if not result["is_correct"]
            else "assisted_correct" if hint_used
            else "perfect_correct"
        )

        sentence_info = sentence_engine.answer_key.get(question_id)
        sentence_data = sentence_engine.bank.get(sentence_info["sentence_id"], {})
        skill_report = learning_engine.get_skill_report(user_id)
        learning_engine.update_progress(
            user_id,
            sentence_info["sentence_id"],
            result["is_correct"],
            result["mistake_type"],
            hint_used=hint_used,
            grammar_focus=sentence_data.get("grammar_focus", []),
        )

        if should_trigger_fsi(
            result["result_type"],
            sentence_info["task_type"],
            sentence_data.get("grammar_focus", []),
            skill_report,
            rng=app.config["fsi_rng"],
        ):
            fsi_tasks = sentence_data.get("fsi_tasks", [])
            if fsi_tasks:
                result["next_immediate_task"] = {
                    "sentence_id": sentence_info["sentence_id"],
                    "task_type": fsi_tasks[0]["task_type"],
                }

        return jsonify(result)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

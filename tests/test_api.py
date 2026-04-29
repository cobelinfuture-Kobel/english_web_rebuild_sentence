import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app


def load_bank_data():
    with open(BASE_DIR / "data" / "sample_sentence_bank.json", encoding="utf-8") as f:
        return json.load(f)


def create_test_client(tmp_path):
    app = create_app(
        sentence_bank=load_bank_data(),
        progress_path=str(tmp_path / "user_progress.json"),
        fsi_rng=lambda: 0.0,
    )
    app.config["TESTING"] = True
    return app.test_client()


def test_health_endpoint_returns_healthy(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "engines": "ready"}


def test_index_page_renders_game_shell(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="game-container"' in html
    assert 'id="status-bar"' in html
    assert 'id="hearts"' in html
    assert 'id="progress-fill"' in html
    assert 'id="score-display"' in html
    assert 'id="fsi-instruction"' in html
    assert 'id="drop-zone"' in html
    assert 'id="pool-zone"' in html
    assert 'id="summary-view"' in html
    assert 'id="mastered-topics"' in html
    assert 'id="bonus-score-note"' in html
    assert 'id="resilience-badge"' in html
    assert 'id="coach-feedback"' in html
    assert 'id="coach-title"' in html
    assert 'id="coach-steps"' in html
    assert 'id="game-over-view"' in html
    assert 'id="coach-feedback-over"' in html
    assert 'id="coach-title-over"' in html
    assert 'id="coach-steps-over"' in html
    assert 'id="mistake-list"' in html
    assert 'id="review-btn"' in html
    assert 'id="replay-voice-btn"' in html
    assert 'id="skill-report-panel"' in html
    assert 'id="weak-skills"' in html
    assert 'id="developing-skills"' in html
    assert 'id="strong-skills"' in html
    assert 'static/js/game.js' in html


def test_index_page_renders_scenario_picker(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="launcher-view"' in html
    assert 'id="level-picker"' in html
    assert "Choose Level" in html
    assert "A1+" in html
    assert "A2+" in html
    assert 'id="game-play-area"' in html
    assert "Daily Routine" in html
    assert "Food & Drink" in html
    assert "Shopping" in html
    assert "Travel & Holiday" in html


def test_index_page_renders_demo_ready_shell(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/?demo=true&level=A1&scenario=shopping&user_id=demo_user")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="launcher-view"' in html
    assert 'id="game-play-area"' in html
    assert 'id="replay-voice-btn"' in html


def test_quest_endpoint_returns_quest_items(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/api/quest", query_string={"user_id": "student_001"})

    assert response.status_code == 200
    body = response.get_json()
    assert "quest_items" in body
    assert body["quest_items"]
    first_item = body["quest_items"][0]
    assert first_item["sentence_id"].startswith("A")
    assert first_item["task_type"] == "original"
    assert first_item["source"] == "new"
    assert isinstance(first_item["grammar_focus"], list)


def test_quest_endpoint_returns_grammar_focus_lists(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/api/quest", query_string={"user_id": "student_001"})

    assert response.status_code == 200
    items = response.get_json()["quest_items"]
    assert all("grammar_focus" in item for item in items)
    assert all(isinstance(item["grammar_focus"], list) for item in items)


def test_quest_endpoint_filters_by_scenario(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get(
        "/api/quest",
        query_string={
            "user_id": "student_001",
            "level": "A1",
            "scenario": "food_drink",
        },
    )

    assert response.status_code == 200
    items = response.get_json()["quest_items"]
    assert items
    assert all(item["sentence_id"].startswith("A1_FOOD_") for item in items)


def test_quest_endpoint_filters_by_level(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get(
        "/api/quest",
        query_string={
            "user_id": "student_001",
            "level": "A2",
        },
    )

    assert response.status_code == 200
    items = response.get_json()["quest_items"]
    assert items
    assert all(item["sentence_id"].startswith("A2_") for item in items)


def test_quest_endpoint_filters_by_level_and_scenario(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get(
        "/api/quest",
        query_string={
            "user_id": "student_001",
            "level": "A2",
            "scenario": "travel_holiday",
        },
    )

    assert response.status_code == 200
    items = response.get_json()["quest_items"]
    assert items
    assert all(item["sentence_id"].startswith("A2_TRAVEL_") for item in items)


def test_question_endpoint_returns_question_payload(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["question_id"]
    assert body["sentence_id"] == "A1_ROUTINE_004"
    assert body["task_type"] == "original"
    assert body["audio_hint_text"] == "I usually drink milk for breakfast."
    assert body["shuffled_chunks"]


def test_skill_report_endpoint_returns_report_for_existing_user(tmp_path):
    client = create_test_client(tmp_path)
    learning_engine = client.application.config["learning_engine"]

    learning_engine.update_progress(
        "student_001",
        "A1_ROUTINE_004",
        True,
        grammar_focus=["present_simple"],
    )
    learning_engine.update_progress(
        "student_001",
        "A1_SHOP_001",
        False,
        mistake_type="word_order_error",
        grammar_focus=["question_structure"],
    )

    response = client.get("/api/report/skills", query_string={"user_id": "student_001"})

    assert response.status_code == 200
    assert response.get_json() == {
        "skills": {
            "present_simple": {
                "score": 2.0,
                "attempts": 1,
                "status": "developing",
            },
            "question_structure": {
                "score": -2.0,
                "attempts": 1,
                "status": "weak",
            },
        }
    }


def test_skill_report_endpoint_returns_empty_dict_for_unknown_user(tmp_path):
    client = create_test_client(tmp_path)

    response = client.get("/api/report/skills", query_string={"user_id": "ghost_user"})

    assert response.status_code == 200
    assert response.get_json() == {"skills": {}}


def test_skill_report_endpoint_updates_after_answer_submission(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    question_response = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    )
    question_payload = question_response.get_json()
    answer_key = app.config["sentence_engine"].answer_key[question_payload["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": answer_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200

    report_response = client.get("/api/report/skills", query_string={"user_id": "student_001"})

    assert report_response.status_code == 200
    assert report_response.get_json() == {
        "skills": {
            "present_simple": {
                "score": 2.0,
                "attempts": 1,
                "status": "developing",
            },
            "adverb_of_frequency": {
                "score": 2.0,
                "attempts": 1,
                "status": "developing",
            },
        }
    }


def test_answer_endpoint_validates_and_updates_progress(tmp_path):
    client = create_test_client(tmp_path)

    question_response = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    )
    question_payload = question_response.get_json()
    correct_ids = [
        chunk["chunk_id"]
        for chunk in sorted(question_payload["shuffled_chunks"], key=lambda chunk: chunk["text"])
    ]

    app = client.application
    answer_key = app.config["sentence_engine"].answer_key[question_payload["question_id"]]
    correct_ids = answer_key["correct_ids"]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": correct_ids,
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200
    body = answer_response.get_json()
    assert body["is_correct"] is True
    assert body["mistake_type"] is None
    assert body["result_type"] == "perfect_correct"

    progress = app.config["learning_engine"].progress["student_001"]["A1_ROUTINE_004"]
    assert progress["attempt_count"] == 1
    assert progress["correct_count"] == 1
    assert progress["last_result"] == "perfect_correct"


def test_answer_endpoint_rejects_invalid_question_id_without_updating_progress(tmp_path):
    client = create_test_client(tmp_path)

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": "missing-question-id",
            "user_chunk_ids": [],
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 400
    assert answer_response.get_json() == {
        "is_correct": False,
        "mistake_type": "invalid_question_id",
    }
    assert client.application.config["learning_engine"].progress == {}


def test_answer_endpoint_returns_fsi_followup_after_correct_original_answer(tmp_path):
    client = create_test_client(tmp_path)

    question_response = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    )
    question_payload = question_response.get_json()
    answer_key = client.application.config["sentence_engine"].answer_key[question_payload["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": answer_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json() == {
        "is_correct": True,
        "mistake_type": None,
        "result_type": "perfect_correct",
        "next_immediate_task": {
            "sentence_id": "A1_ROUTINE_004",
            "task_type": "question",
        },
    }


def test_answer_endpoint_does_not_return_fsi_followup_after_wrong_answer(tmp_path):
    client = create_test_client(tmp_path)

    question_response = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    )
    question_payload = question_response.get_json()
    answer_key = client.application.config["sentence_engine"].answer_key[question_payload["question_id"]]
    wrong_ids = list(reversed(answer_key["correct_ids"]))

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": wrong_ids,
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json() == {
        "is_correct": False,
        "mistake_type": "word_order_error",
        "result_type": "incorrect",
    }


def test_answer_endpoint_triggers_fsi_for_weak_grammar(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    warmup_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    warmup_key = app.config["sentence_engine"].answer_key[warmup_question["question_id"]]

    client.post(
        "/api/answer",
        json={
            "question_id": warmup_question["question_id"],
            "user_chunk_ids": list(reversed(warmup_key["correct_ids"])),
            "user_id": "student_001",
        },
    )

    followup_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    followup_key = app.config["sentence_engine"].answer_key[followup_question["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": followup_question["question_id"],
            "user_chunk_ids": followup_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json()["next_immediate_task"] == {
        "sentence_id": "A1_ROUTINE_004",
        "task_type": "question",
    }


def test_answer_endpoint_does_not_trigger_fsi_for_assisted_correct(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    question_payload = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    answer_key = app.config["sentence_engine"].answer_key[question_payload["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": answer_key["correct_ids"],
            "user_id": "student_001",
            "hint_used": True,
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json() == {
        "is_correct": True,
        "mistake_type": None,
        "result_type": "assisted_correct",
    }


def test_answer_endpoint_does_not_trigger_fsi_for_non_original_task(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    question_payload = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "question"},
    ).get_json()
    answer_key = app.config["sentence_engine"].answer_key[question_payload["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": question_payload["question_id"],
            "user_chunk_ids": answer_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json() == {
        "is_correct": True,
        "mistake_type": None,
        "result_type": "perfect_correct",
    }


def test_answer_endpoint_tracks_multiple_attempts_for_same_user(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    first_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    first_key = app.config["sentence_engine"].answer_key[first_question["question_id"]]
    wrong_ids = list(reversed(first_key["correct_ids"]))

    first_answer = client.post(
        "/api/answer",
        json={
            "question_id": first_question["question_id"],
            "user_chunk_ids": wrong_ids,
            "user_id": "student_001",
        },
    )

    assert first_answer.status_code == 200
    assert first_answer.get_json()["is_correct"] is False

    second_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    second_key = app.config["sentence_engine"].answer_key[second_question["question_id"]]

    second_answer = client.post(
        "/api/answer",
        json={
            "question_id": second_question["question_id"],
            "user_chunk_ids": second_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    assert second_answer.status_code == 200
    assert second_answer.get_json()["is_correct"] is True
    assert second_answer.get_json()["result_type"] == "perfect_correct"

    progress = app.config["learning_engine"].progress["student_001"]["A1_ROUTINE_004"]
    assert progress["attempt_count"] == 2
    assert progress["correct_count"] == 1
    assert progress["mistake_count"] == 1
    assert progress["last_result"] == "perfect_correct"


def test_answer_endpoint_marks_assisted_correct_and_keeps_srs_level(tmp_path):
    client = create_test_client(tmp_path)
    app = client.application

    first_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    first_key = app.config["sentence_engine"].answer_key[first_question["question_id"]]

    client.post(
        "/api/answer",
        json={
            "question_id": first_question["question_id"],
            "user_chunk_ids": first_key["correct_ids"],
            "user_id": "student_001",
        },
    )

    second_question = client.get(
        "/api/question",
        query_string={"sentence_id": "A1_ROUTINE_004", "task_type": "original"},
    ).get_json()
    second_key = app.config["sentence_engine"].answer_key[second_question["question_id"]]

    answer_response = client.post(
        "/api/answer",
        json={
            "question_id": second_question["question_id"],
            "user_chunk_ids": second_key["correct_ids"],
            "user_id": "student_001",
            "hint_used": True,
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.get_json()["result_type"] == "assisted_correct"

    progress = app.config["learning_engine"].progress["student_001"]["A1_ROUTINE_004"]
    assert progress["srs_level"] == 1
    assert progress["last_result"] == "assisted_correct"
    assert progress["last_hint_used"] is True

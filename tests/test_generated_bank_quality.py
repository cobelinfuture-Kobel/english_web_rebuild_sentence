import json
from pathlib import Path

from scripts.validate_generated_bank import validate_generated_bank


def make_valid_sentence(**overrides):
    sentence = {
        "sentence_id": "A1_SHOPPING_SHOP_WANT_001",
        "level": "A1",
        "scenario": "shopping",
        "target_sentence": "I want this shirt.",
        "chunks": ["I want", "this shirt", "."],
        "grammar_focus": ["present_simple", "demonstratives"],
        "fsi_tasks": [
            {
                "task_type": "question",
                "target": "Do you want this shirt?",
                "chunks": ["Do you want", "this shirt", "?"],
            }
        ],
    }
    sentence.update(overrides)
    return sentence


def test_validate_generated_bank_accepts_valid_data():
    result = validate_generated_bank(
        [
            make_valid_sentence(),
            make_valid_sentence(
                sentence_id="A1_SHOPPING_SHOP_WANT_002",
                target_sentence="I want this jacket.",
                chunks=["I want", "this jacket", "."],
                fsi_tasks=[],
            ),
            make_valid_sentence(
                sentence_id="A1_SHOPPING_SHOP_PRICE_001",
                target_sentence="How much is this shirt?",
                chunks=["How much is", "this shirt", "?"],
                grammar_focus=["wh_questions", "demonstratives"],
                fsi_tasks=[],
            ),
        ]
    )

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_validate_generated_bank_rejects_duplicate_sentence_ids():
    result = validate_generated_bank(
        [make_valid_sentence(), make_valid_sentence(target_sentence="I want this jacket.")]
    )

    assert result["is_valid"] is False
    assert any("Duplicate sentence_id" in error for error in result["errors"])


def test_validate_generated_bank_rejects_duplicate_target_sentences():
    result = validate_generated_bank(
        [
            make_valid_sentence(),
            make_valid_sentence(
                sentence_id="A1_SHOPPING_SHOP_WANT_002",
                chunks=["I want", "this jacket", "."],
            ),
        ]
    )

    assert result["is_valid"] is False
    assert any("Duplicate target_sentence" in error for error in result["errors"])


def test_validate_generated_bank_rejects_empty_chunks():
    result = validate_generated_bank([make_valid_sentence(chunks=[])])

    assert result["is_valid"] is False
    assert any("chunks" in error for error in result["errors"])


def test_validate_generated_bank_rejects_invalid_grammar_tag():
    result = validate_generated_bank(
        [make_valid_sentence(grammar_focus=["present_simple", "not_a_real_tag"])]
    )

    assert result["is_valid"] is False
    assert any("Invalid grammar tag" in error for error in result["errors"])


def test_validate_generated_bank_rejects_broken_fsi_task():
    result = validate_generated_bank(
        [
            make_valid_sentence(
                fsi_tasks=[
                    {
                        "task_type": "question",
                        "target": "Do you want this shirt?",
                        "chunks": [],
                    }
                ]
            )
        ]
    )

    assert result["is_valid"] is False
    assert any("Invalid fsi_task" in error for error in result["errors"])


def test_generated_shopping_bank_is_clean():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    result = validate_generated_bank(data)

    assert result["is_valid"] is True, result["errors"]

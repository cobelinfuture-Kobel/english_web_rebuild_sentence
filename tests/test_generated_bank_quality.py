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


def test_generated_shopping_bank_has_no_pay_by_targets():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert all("Can I pay by " not in sentence["target_sentence"] for sentence in data)


def test_generated_shopping_bank_has_no_plural_buy_it_mismatch():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert all("these " not in sentence["target_sentence"] or "before I buy it" not in sentence["target_sentence"] for sentence in data)


def test_generated_shopping_bank_has_no_lowercase_demonstrative_sentence_starts():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert all(not sentence["target_sentence"].startswith("this ") for sentence in data)


def test_generated_shopping_bank_a2_plus_want_uses_singular_positive_reasons():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    want_targets = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["level"] == "A2+" and sentence["pattern_id"] == "SHOP_WANT"
    ]

    assert want_targets
    assert all("these " not in target for target in want_targets)
    assert all(
        blocked not in target
        for target in want_targets
        for blocked in (" old.", " dirty.", " expensive.", " cold.", " loose.", " rough.")
    )


def test_generated_shopping_bank_too_targets_come_from_pairs():
    path = Path("data/generated/shopping_sentence_bank.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    slot_bank = json.loads(Path("data/slot_bank/shopping_slots.json").read_text(encoding="utf-8"))
    pair_targets_a2 = {
        f"I think {item['object']} is too {item['adjective']}."
        for item in slot_bank["too_item_adjective_pairs"]
    }
    pair_targets_a2_plus = {
        f"{item['subject']} is too {item['adjective']} for me."
        for item in slot_bank["too_item_adjective_pairs"]
    }

    a2_targets = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["level"] == "A2" and sentence["pattern_id"] == "SHOP_TOO"
    ]
    a2_plus_targets = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["level"] == "A2+" and sentence["pattern_id"] == "SHOP_TOO"
    ]

    assert all(target in pair_targets_a2 for target in a2_targets)
    assert all(target in pair_targets_a2_plus for target in a2_plus_targets)

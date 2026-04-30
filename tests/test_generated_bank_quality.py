import json
import re
from collections import Counter
from pathlib import Path

from scripts.validate_generated_bank import validate_generated_bank


GENERATED_BANK_PATH = Path("data/generated/shopping_sentence_bank.json")


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


def load_generated_shopping_bank():
    return json.loads(GENERATED_BANK_PATH.read_text(encoding="utf-8"))


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
    data = load_generated_shopping_bank()

    result = validate_generated_bank(data, min_per_group=1)

    assert result["is_valid"] is True, result["errors"]


def test_generated_shopping_bank_target_sentences_are_unique():
    data = load_generated_shopping_bank()
    targets = [sentence["target_sentence"] for sentence in data]
    duplicates = sorted(
        target for target, count in Counter(targets).items() if count > 1
    )

    assert len(targets) == len(set(targets)), f"Duplicate target_sentence values: {duplicates}"


def test_generated_shopping_bank_has_no_pay_by_targets():
    data = load_generated_shopping_bank()

    assert all("Can I pay by " not in sentence["target_sentence"] for sentence in data)
    assert all(
        "Can I pay by " not in task["target"]
        for sentence in data
        for task in sentence.get("fsi_tasks", [])
    )


def test_generated_shopping_bank_has_no_plural_buy_it_mismatch():
    data = load_generated_shopping_bank()

    assert all("these " not in sentence["target_sentence"] or "before I buy it" not in sentence["target_sentence"] for sentence in data)


def test_generated_shopping_bank_has_no_lowercase_sentence_starts():
    data = load_generated_shopping_bank()

    assert all(sentence["target_sentence"][0].isupper() for sentence in data)


def test_generated_shopping_bank_a2_plus_want_uses_singular_positive_reasons():
    data = load_generated_shopping_bank()

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
    data = load_generated_shopping_bank()
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


def test_generated_shopping_bank_has_no_british_english_shopping_terms():
    data = load_generated_shopping_bank()
    blocked_terms = (
        "shop assistant",
        "till",
        "queue",
        "chemist",
        "jumper",
        "trainers",
        "guarantee",
    )

    assert all(
        re.search(rf"\b{re.escape(blocked_term)}\b", sentence["target_sentence"].lower()) is None
        for sentence in data
        for blocked_term in blocked_terms
    )


def test_generated_shopping_bank_a1_has_no_higher_level_structures():
    data = load_generated_shopping_bank()
    blocked_terms = (
        "because",
        "after the discount",
        "before i buy it",
        "in another color",
        "in a different color",
        "refund",
        "exchange",
        "warranty",
        "made of",
        "return",
    )

    a1_targets = [sentence["target_sentence"].lower() for sentence in data if sentence["level"] == "A1"]
    assert all(blocked not in target for target in a1_targets for blocked in blocked_terms)


def test_generated_shopping_bank_a1_plus_has_no_b1_terms():
    data = load_generated_shopping_bank()
    blocked_terms = ("refund", "exchange", "warranty", "made of")

    a1_plus_targets = [sentence["target_sentence"].lower() for sentence in data if sentence["level"] == "A1+"]
    assert all(blocked not in target for target in a1_plus_targets for blocked in blocked_terms)


def test_generated_shopping_bank_size_patterns_only_use_clothing_items():
    data = load_generated_shopping_bank()
    blocked_items = ("pen", "pencil", "eraser", "ruler", "notebook", "gift box")
    size_targets = [
        sentence["target_sentence"].lower()
        for sentence in data
        if sentence["pattern_id"] in {"SHOP_SIZE_HAVE", "SHOP_EXCHANGE_SIZE"}
    ]

    assert all(blocked not in target for target in size_targets for blocked in blocked_items)


def test_generated_shopping_bank_damage_targets_come_from_pairs():
    data = load_generated_shopping_bank()
    slot_bank = json.loads(Path("data/slot_bank/shopping_slots.json").read_text(encoding="utf-8"))
    damage_targets = {
        f"{item['subject']} {item['issue']}."
        for item in slot_bank["damaged_item_pairs"]
    }
    damage_return_targets = {
        f"I'd like to return {item['object']} because it {item['issue']}."
        for item in slot_bank["damaged_item_pairs"]
    }

    generated_damage = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["pattern_id"] == "SHOP_DAMAGE"
    ]
    generated_damage_return = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["pattern_id"] == "SHOP_DAMAGE_RETURN"
    ]

    assert all(target in damage_targets for target in generated_damage)
    assert all(target in damage_return_targets for target in generated_damage_return)


def test_generated_shopping_bank_material_targets_come_from_pairs():
    data = load_generated_shopping_bank()
    slot_bank = json.loads(Path("data/slot_bank/shopping_slots.json").read_text(encoding="utf-8"))
    material_targets = {
        f"Is {item['object']} made of {item['material']}?"
        for item in slot_bank["material_item_pairs"]
    }

    generated_targets = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["pattern_id"] == "SHOP_MATERIAL"
    ]

    assert all(target in material_targets for target in generated_targets)


def test_generated_shopping_bank_a2_plus_take_uses_needed_items_only():
    data = load_generated_shopping_bank()

    take_targets = [
        sentence["target_sentence"]
        for sentence in data
        if sentence["level"] == "A2+" and sentence["pattern_id"] == "SHOP_TAKE"
    ]

    assert take_targets
    blocked_targets = (
        "this card because I need it",
        "the blue one because I need it",
        "this toy because I need it",
        "this gift box because I need it",
        "this key ring because I need it",
        "this ball because I need it",
        "this watch because I need it",
        "this cup because I need it",
        "this blue cup because I need it",
    )
    assert all(blocked not in target.lower() for target in take_targets for blocked in blocked_targets)


def test_generated_shopping_bank_sentence_id_level_prefix_matches_level_field():
    data = load_generated_shopping_bank()
    mismatches = []

    for sentence in data:
        expected_prefix = f"{sentence['level']}_"
        if not sentence["sentence_id"].startswith(expected_prefix):
            mismatches.append(
                f"{sentence['sentence_id']} has level={sentence['level']}"
            )

    assert not mismatches, f"sentence_id / level mismatches: {mismatches}"


def test_generated_shopping_bank_shop_too_uses_approved_semantic_pairs():
    data = load_generated_shopping_bank()
    approved_pairs = {
        ("this shirt", "small"),
        ("this jacket", "big"),
        ("this water bottle", "heavy"),
        ("this cup", "small"),
        ("this coat", "heavy"),
        ("this pen", "expensive"),
        ("this hat", "small"),
        ("this cap", "tight"),
        ("this notebook", "thick"),
        ("this skirt", "short"),
        ("this dress", "long"),
        ("this sweater", "thick"),
        ("this school bag", "heavy"),
        ("this umbrella", "long"),
        ("this black bag", "big"),
        ("this red bag", "heavy"),
        ("this pencil case", "small"),
        ("this t-shirt", "thin"),
    }
    parse_failures = []
    invalid_pairs = []

    for sentence in data:
        if sentence["pattern_id"] != "SHOP_TOO" or sentence["level"] not in {"A1+", "A2", "A2+"}:
            continue

        text = sentence["target_sentence"].strip().rstrip(".!?").lower()
        if text.startswith("i think "):
            text = text[len("i think "):]
        if text.endswith(" for me"):
            text = text[: -len(" for me")]

        if " is too " not in text:
            parse_failures.append(
                f"{sentence['sentence_id']}: {sentence['target_sentence']}"
            )
            continue

        obj, adjective = text.split(" is too ", 1)
        pair = (obj.strip(), adjective.strip())
        if pair not in approved_pairs:
            invalid_pairs.append(
                f"{sentence['sentence_id']}: {sentence['target_sentence']}"
            )

    assert not parse_failures, f"Unparseable SHOP_TOO sentences: {parse_failures}"
    assert not invalid_pairs, f"SHOP_TOO sentences with unapproved pairs: {invalid_pairs}"

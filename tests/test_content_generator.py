import json
import random
from pathlib import Path

import pytest

from engines.sentence_engine import SentenceEngine
from scripts.generate_sentences import ContentGenerator


BASE_DIR = Path(__file__).resolve().parent.parent
PATTERN_BANK_PATH = BASE_DIR / "data" / "pattern_bank" / "shopping_patterns.json"
SLOT_BANK_PATH = BASE_DIR / "data" / "slot_bank" / "shopping_slots.json"

EXPECTED_PATTERNS = {
    "SHOP_WANT",
    "SHOP_LIKE",
    "SHOP_PRICE",
    "SHOP_HAVE",
    "SHOP_TRY",
    "SHOP_TOO",
    "SHOP_TAKE",
    "SHOP_WHERE",
    "SHOP_PAY",
    "SHOP_LOOKING",
}
EXPECTED_LEVELS = {"A1", "A1+", "A2"}


def load_banks():
    return (
        json.loads(PATTERN_BANK_PATH.read_text(encoding="utf-8")),
        json.loads(SLOT_BANK_PATH.read_text(encoding="utf-8")),
    )


def make_generator(seed=7, ensure_unique_targets=False):
    pattern_bank, slot_bank = load_banks()
    return ContentGenerator(
        pattern_bank=pattern_bank,
        slot_bank=slot_bank,
        rng=random.Random(seed),
        ensure_unique_targets=ensure_unique_targets,
    )


def make_unsupported_fsi_bank():
    return {
        "SHOP_TRY": {
            "pattern_id": "SHOP_TRY",
            "function": "trying_items",
            "variants": {
                "A1": {
                    "example_template": "Can I try on {object}?",
                    "chunks_template": ["Can I try on", "{object}", "?"],
                    "slot_constraints": {
                        "object": {
                            "category": ["wearable_items"],
                            "wearable": True,
                        }
                    },
                    "grammar_focus": ["can_request", "shopping_actions"],
                    "fsi_rules": ["negative", "unsupported_rule"],
                    "complexity": {"depth": 1},
                }
            },
        }
    }


def make_small_slot_bank():
    return {
        "wearable_items": [
            {
                "text": "this shirt",
                "plural": False,
                "wearable": True,
                "priceable": True,
            },
            {
                "text": "milk",
                "plural": False,
                "wearable": False,
                "priceable": True,
            },
        ]
    }


def test_generate_for_pattern_returns_sentence_list():
    generator = make_generator(seed=7)

    sentences = generator.generate_for_pattern("SHOP_WANT", "A1", count=3)

    assert len(sentences) == 3
    assert all(sentence["pattern_id"] == "SHOP_WANT" for sentence in sentences)


def test_generated_sentences_have_required_fields():
    generator = make_generator(seed=3)

    sentence = generator.generate_for_pattern("SHOP_WANT", "A1", count=1)[0]

    assert sentence["sentence_id"]
    assert sentence["level"] == "A1"
    assert sentence["scenario"] == "shopping"
    assert sentence["target_sentence"]
    assert sentence["chunks"]
    assert sentence["grammar_focus"]
    assert isinstance(sentence["fsi_tasks"], list)


def test_pattern_coverage_in_generated_bank():
    generator = make_generator(seed=5, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)

    assert {sentence["pattern_id"] for sentence in sentences} == EXPECTED_PATTERNS


def test_level_coverage_for_each_pattern():
    generator = make_generator(seed=11, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)
    by_pattern = {}
    for sentence in sentences:
        by_pattern.setdefault(sentence["pattern_id"], set()).add(sentence["level"])

    assert all(by_pattern[pattern_id] == EXPECTED_LEVELS for pattern_id in EXPECTED_PATTERNS)


def test_shop_try_only_uses_wearable_objects():
    generator = make_generator(seed=13)
    slot_bank = generator.slot_bank
    disallowed = {
        item["text"]
        for group in slot_bank.values()
        for item in group
        if item.get("wearable") is False
    }

    sentences = generator.generate_for_pattern("SHOP_TRY", "A1", count=20)

    assert sentences
    assert all(
        all(text not in sentence["target_sentence"] for text in disallowed)
        for sentence in sentences
    )


def test_shop_price_matches_is_are_with_plurality():
    generator = make_generator(seed=17)
    plural_lookup = {}
    for group_name in ("priceable_single", "priceable_plural"):
        for item in generator.slot_bank[group_name]:
            plural_lookup[item["text"]] = item["plural"]

    sentences = []
    for level in EXPECTED_LEVELS:
        sentences.extend(generator.generate_for_pattern("SHOP_PRICE", level, count=10))

    assert sentences
    for sentence in sentences:
        matched_object = next(
            text for text in plural_lookup
            if text in sentence["target_sentence"]
        )
        if "How much are" in sentence["target_sentence"]:
            assert plural_lookup[matched_object] is True
        if "How much is" in sentence["target_sentence"]:
            assert plural_lookup[matched_object] is False


def test_validate_sentence_rejects_empty_chunks():
    generator = make_generator(seed=1)

    with pytest.raises(ValueError, match="chunks"):
        generator._validate_sentence(
            {
                "sentence_id": "A1_SHOPPING_SHOP_WANT_001",
                "level": "A1",
                "scenario": "shopping",
                "pattern_id": "SHOP_WANT",
                "target_sentence": "I want this shirt.",
                "chunks": [],
                "translation": "",
                "grammar_focus": ["present_simple"],
                "difficulty_score": 1,
                "fsi_tasks": [],
            }
        )


def test_validate_sentence_rejects_empty_grammar_focus():
    generator = make_generator(seed=1)

    with pytest.raises(ValueError, match="grammar_focus"):
        generator._validate_sentence(
            {
                "sentence_id": "A1_SHOPPING_SHOP_WANT_001",
                "level": "A1",
                "scenario": "shopping",
                "pattern_id": "SHOP_WANT",
                "target_sentence": "I want this shirt.",
                "chunks": ["I want", "this shirt"],
                "translation": "",
                "grammar_focus": [],
                "difficulty_score": 1,
                "fsi_tasks": [],
            }
        )


def test_unsupported_fsi_rule_is_skipped_safely():
    generator = ContentGenerator(
        make_unsupported_fsi_bank(),
        make_small_slot_bank(),
        rng=random.Random(2),
    )

    sentence = generator.generate_for_pattern("SHOP_TRY", "A1", count=1)[0]

    assert [task["task_type"] for task in sentence["fsi_tasks"]] == ["negative"]


def test_injected_rng_makes_generation_predictable():
    generator_one = make_generator(seed=19)
    generator_two = make_generator(seed=19)

    sentences_one = generator_one.generate_for_pattern("SHOP_WANT", "A1", count=4)
    sentences_two = generator_two.generate_for_pattern("SHOP_WANT", "A1", count=4)

    assert sentences_one == sentences_two


def test_generate_all_produces_at_least_120_unique_sentences():
    generator = make_generator(seed=23, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)

    ids = [sentence["sentence_id"] for sentence in sentences]
    targets = [sentence["target_sentence"] for sentence in sentences]

    assert len(sentences) >= 120
    assert len(ids) == len(set(ids))
    assert len(targets) == len(set(targets))


def test_sentence_ids_are_unique_and_output_loads_into_sentence_engine():
    generator = make_generator(seed=29, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)
    ids = [sentence["sentence_id"] for sentence in sentences]

    engine = SentenceEngine(sentences)
    payload = engine.get_question_payload(ids[0], "original")

    assert len(ids) == len(set(ids))
    assert payload["sentence_id"] == ids[0]

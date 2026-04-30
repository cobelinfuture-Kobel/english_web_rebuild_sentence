import json
import random
from pathlib import Path

import pytest

from engines.sentence_engine import SentenceEngine
from scripts.generate_sentences import (
    COUNT_BY_PATTERN_LEVEL,
    ContentGenerator,
    DEFAULT_COUNT_PER_VARIANT,
)


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
EXPECTED_LEVELS = {"A1", "A1+", "A2", "A2+"}


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
    wearable_lookup = {
        item["text"]: item["wearable"]
        for item in generator.slot_bank["wearable_items"]
    }

    sentences = generator.generate_for_pattern("SHOP_TRY", "A1", count=20)

    assert sentences
    for sentence in sentences:
        matched_object = next(
            text
            for text in sorted(wearable_lookup, key=len, reverse=True)
            if text in sentence["target_sentence"]
        )
        assert wearable_lookup[matched_object] is True


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


def test_unique_generation_returns_available_sentences_when_count_exceeds_supply():
    generator = ContentGenerator(
        make_unsupported_fsi_bank(),
        make_small_slot_bank(),
        rng=random.Random(2),
        ensure_unique_targets=True,
    )

    sentences = generator.generate_for_pattern("SHOP_TRY", "A1", count=5)

    assert len(sentences) == 1
    assert sentences[0]["target_sentence"] == "Can I try on this shirt?"


def test_injected_rng_makes_generation_predictable():
    generator_one = make_generator(seed=19)
    generator_two = make_generator(seed=19)

    sentences_one = generator_one.generate_for_pattern("SHOP_WANT", "A1", count=4)
    sentences_two = generator_two.generate_for_pattern("SHOP_WANT", "A1", count=4)

    assert sentences_one == sentences_two


def test_generate_all_produces_at_least_200_unique_sentences():
    generator = make_generator(seed=23, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)

    ids = [sentence["sentence_id"] for sentence in sentences]
    targets = [sentence["target_sentence"] for sentence in sentences]

    assert len(sentences) >= 200
    assert len(ids) == len(set(ids))
    assert len(targets) == len(set(targets))


def test_generate_all_supports_30_unique_sentences_per_variant():
    generator = make_generator(seed=47, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=DEFAULT_COUNT_PER_VARIANT)

    ids = [sentence["sentence_id"] for sentence in sentences]
    targets = [sentence["target_sentence"] for sentence in sentences]

    expected_total = (len(EXPECTED_PATTERNS) * len(EXPECTED_LEVELS) * DEFAULT_COUNT_PER_VARIANT) - (
        (DEFAULT_COUNT_PER_VARIANT - COUNT_BY_PATTERN_LEVEL[("SHOP_TOO", "A1")])
        + (DEFAULT_COUNT_PER_VARIANT - COUNT_BY_PATTERN_LEVEL[("SHOP_PAY", "A1")])
        + (DEFAULT_COUNT_PER_VARIANT - COUNT_BY_PATTERN_LEVEL[("SHOP_TOO", "A1+")])
        + (DEFAULT_COUNT_PER_VARIANT - COUNT_BY_PATTERN_LEVEL[("SHOP_PAY", "A1+")])
        + (DEFAULT_COUNT_PER_VARIANT - COUNT_BY_PATTERN_LEVEL[("SHOP_LOOKING", "A1+")])
    )

    assert len(sentences) == expected_total
    assert len(ids) == len(set(ids))
    assert len(targets) == len(set(targets))


def test_each_pattern_has_a2_plus_variant():
    pattern_bank, _ = load_banks()

    assert all("A2+" in pattern_bank[pattern_id]["variants"] for pattern_id in EXPECTED_PATTERNS)


def test_a2_plus_generated_sentences_are_not_empty():
    generator = make_generator(seed=31, ensure_unique_targets=True)

    sentences = []
    for pattern_id in EXPECTED_PATTERNS:
        sentences.extend(generator.generate_for_pattern(pattern_id, "A2+", count=5))

    assert sentences
    assert all(sentence["level"] == "A2+" for sentence in sentences)


def test_shop_try_a2_plus_only_uses_wearable_objects():
    generator = make_generator(seed=37)
    wearable_lookup = {
        item["text"]: item["wearable"]
        for item in generator.slot_bank["wearable_items"]
    }

    sentences = generator.generate_for_pattern("SHOP_TRY", "A2+", count=20)

    assert sentences
    for sentence in sentences:
        matched_object = next(
            text
            for text in sorted(wearable_lookup, key=len, reverse=True)
            if text in sentence["target_sentence"]
        )
        assert wearable_lookup[matched_object] is True


def test_shop_price_a2_plus_how_much_is_only_uses_singular_objects():
    generator = make_generator(seed=41)
    plural_lookup = {}
    for group_name in ("priceable_single", "priceable_plural"):
        for item in generator.slot_bank[group_name]:
            plural_lookup[item["text"]] = item["plural"]

    sentences = generator.generate_for_pattern("SHOP_PRICE", "A2+", count=20)

    assert sentences
    for sentence in sentences:
        if "How much is" not in sentence["target_sentence"]:
            continue
        matched_object = next(
            text for text in plural_lookup
            if text in sentence["target_sentence"]
        )
        assert plural_lookup[matched_object] is False


def test_shop_pay_a1_uses_with_for_target_and_fsi_question():
    generator = make_generator(seed=43)

    sentence = generator.generate_for_pattern("SHOP_PAY", "A1", count=1)[0]

    assert sentence["target_sentence"].startswith("Can I pay with ")
    assert sentence["chunks"][0] == "Can I pay with"
    assert sentence["fsi_tasks"][0]["target"].startswith("Can I pay with ")
    assert sentence["fsi_tasks"][0]["chunks"][0] == "Can I pay with"


def test_generate_all_uses_pattern_level_count_overrides():
    generator = make_generator(seed=53, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=DEFAULT_COUNT_PER_VARIANT)
    counts = {}
    for sentence in sentences:
        counts[(sentence["pattern_id"], sentence["level"])] = (
            counts.get((sentence["pattern_id"], sentence["level"]), 0) + 1
        )

    assert counts[("SHOP_TOO", "A1")] == 24
    assert counts[("SHOP_PAY", "A1")] == 16
    assert counts[("SHOP_TOO", "A1+")] == 18
    assert counts[("SHOP_PAY", "A1+")] == 16
    assert counts[("SHOP_LOOKING", "A1+")] == 15
    assert counts[("SHOP_WANT", "A2")] == DEFAULT_COUNT_PER_VARIANT


def test_shop_pay_a1_plus_uses_with_payment_methods_with():
    generator = make_generator(seed=59)

    sentence = generator.generate_for_pattern("SHOP_PAY", "A1+", count=1)[0]

    assert sentence["target_sentence"].startswith("Can I pay for ")
    assert " with " in sentence["target_sentence"]
    assert " by " not in sentence["target_sentence"]
    assert sentence["chunks"][2] == "with"


def test_shop_looking_a1_plus_only_uses_school_items():
    generator = make_generator(seed=61)
    school_items = {item["text"] for item in generator.slot_bank["school_items_single"]}

    sentences = generator.generate_for_pattern("SHOP_LOOKING", "A1+", count=15)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"].startswith("I am looking for ")
        matched_object = next(item for item in school_items if item in sentence["target_sentence"])
        assert matched_object in school_items


def test_shop_too_a1_plus_uses_paired_capitalized_subjects():
    generator = make_generator(seed=67, ensure_unique_targets=True)
    valid_targets = {
        f"{item['subject']} is too {item['adjective']}."
        for item in generator.slot_bank["too_item_adjective_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_TOO", "A1+", count=18)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets
        assert sentence["target_sentence"].startswith("This ")


def test_sentence_ids_are_unique_and_output_loads_into_sentence_engine():
    generator = make_generator(seed=29, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)
    ids = [sentence["sentence_id"] for sentence in sentences]

    engine = SentenceEngine(sentences)
    payload = engine.get_question_payload(ids[0], "original")

    assert len(ids) == len(set(ids))
    assert payload["sentence_id"] == ids[0]

import json
import random
from collections import Counter
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
FOOD_PATTERN_BANK_PATH = BASE_DIR / "data" / "pattern_bank" / "food_drink_patterns.json"
FOOD_SLOT_BANK_PATH = BASE_DIR / "data" / "slot_bank" / "food_drink_slots.json"
DAILY_ROUTINE_SENTENCE_BANK_PATH = (
    BASE_DIR / "data" / "generated" / "daily_routine_sentence_bank.json"
)
DAILY_ROUTINE_PHASE5_PLAN_PATH = (
    BASE_DIR / "docs" / "daily_routine_phase5_grammar_aware_agreement_plan.md"
)
DAILY_ROUTINE_PHASE4C_A_NOTES_PATH = (
    BASE_DIR / "docs" / "daily_routine_phase4c_a_completion_notes.md"
)
DAILY_ROUTINE_PHASE4C_B_NOTES_PATH = (
    BASE_DIR / "docs" / "daily_routine_phase4c_b_metadata_cleanup_notes.md"
)

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
    "SHOP_SIZE_HAVE",
    "SHOP_SIZE_TRY",
    "SHOP_SALE",
    "SHOP_RECEIPT",
    "SHOP_CHEAPER",
    "SHOP_CHEAPEST",
    "SHOP_COMPARE",
    "SHOP_ANOTHER_COLOR",
    "SHOP_RECOMMEND",
    "SHOP_LOOKS_BETTER",
    "SHOP_RETURN",
    "SHOP_EXCHANGE_SIZE",
    "SHOP_REFUND",
    "SHOP_DAMAGE",
    "SHOP_DAMAGE_RETURN",
    "SHOP_RECEIPT_REFUND",
    "SHOP_WARRANTY",
    "SHOP_QUALITY",
    "SHOP_MATERIAL",
}
CORE_EXPECTED_LEVELS = {"A1", "A1+", "A2", "A2+"}
CORE_PATTERNS = {
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
B1_PATTERNS = {
    "SHOP_RETURN",
    "SHOP_EXCHANGE_SIZE",
    "SHOP_REFUND",
    "SHOP_DAMAGE",
    "SHOP_DAMAGE_RETURN",
    "SHOP_RECEIPT_REFUND",
    "SHOP_WARRANTY",
    "SHOP_QUALITY",
    "SHOP_MATERIAL",
}
EXPECTED_FOOD_PATTERNS = {
    "FOOD_WANT_COUNTABLE",
    "FOOD_WANT_UNCOUNTABLE",
    "FOOD_CHOICE",
    "FOOD_MEASURE_WANT",
    "FOOD_MEASURE_HAVE",
    "FOOD_LIKE",
    "FOOD_HAVE",
    "FOOD_PRICE",
    "FOOD_STATE",
    "FOOD_TOO",
    "FOOD_EAT",
    "FOOD_ASK_WANT",
    "FOOD_DRINK",
    "FOOD_DONT_WANT",
    "FOOD_HAVE_POLITE",
    "FOOD_HAVE_STOCK",
    "FOOD_BREAKFAST",
    "FOOD_LUNCH",
    "FOOD_DINNER",
    "FOOD_SNACK",
    "FOOD_TO_GO",
    "FOOD_ORDER",
    "FOOD_REQUEST",
    "FOOD_ANY_HAVE",
    "FOOD_NO_ICE",
    "FOOD_LESS_SUGAR",
    "FOOD_RESTROOM",
    "FOOD_WHERE_ITEM",
    "FOOD_LIKE_REASON",
    "FOOD_WANT_REASON",
    "FOOD_NOT_WANT_REASON",
    "FOOD_RECOMMEND",
    "FOOD_RECOMMEND_CONTEXT",
    "FOOD_INGREDIENT",
    "FOOD_SUBSTITUTE",
    "FOOD_PREFER_MORE",
    "FOOD_RESERVATION",
    "FOOD_TABLE",
    "FOOD_ORDER_DETAIL",
    "FOOD_WITHOUT",
    "FOOD_ALLERGY",
    "FOOD_INGREDIENT_DETAIL",
    "FOOD_VEGETARIAN_RECOMMEND",
    "FOOD_PROBLEM",
    "FOOD_REPLACEMENT",
    "FOOD_CHECK",
    "FOOD_SPLIT_CHECK",
    "FOOD_PAY_SEPARATELY",
}
EXPECTED_DAILY_ROUTINE_PHASE4B_PATTERNS = {
    "ROUTINE_HAVE_ITEM",
    "ROUTINE_READY",
    "ROUTINE_SIMPLE_TIME",
    "ROUTINE_PACK",
    "ROUTINE_HELP_SIMPLE",
    "ROUTINE_CHORE_SIMPLE",
    "ROUTINE_PUT_ON",
    "ROUTINE_ASK_TIME",
    "ROUTINE_ASK_WHAT_DO",
    "ROUTINE_ASK_WHEN_DO",
    "ROUTINE_READY_FOR",
    "ROUTINE_LATE_FOR",
    "ROUTINE_FORGOT",
    "ROUTINE_PERMISSION",
    "ROUTINE_HELP_REASON",
    "ROUTINE_CHORE_REASON",
    "ROUTINE_REMIND",
    "ROUTINE_CANNOT_NOW",
    "ROUTINE_TIME_TAKES",
    "ROUTINE_SHOULD",
    "ROUTINE_PARENT_RULE",
    "ROUTINE_BEFORE_LEAVE",
    "ROUTINE_AFTER_FINISH",
}
EXPECTED_DAILY_ROUTINE_PHASE4C_PATTERNS = {
    "ROUTINE_HAVE_ITEM_FSI",
    "ROUTINE_CLEAN_OBJECT",
    "ROUTINE_BRUSH_OBJECT",
    "ROUTINE_WASH_OBJECT",
    "ROUTINE_PACK_ITEM_FSI",
    "ROUTINE_GET_ITEM",
    "ROUTINE_CLEAN_OBJECT_TIME",
    "ROUTINE_PACK_ITEM_TIME",
    "ROUTINE_PUT_ON_ITEM_TIME",
    "ROUTINE_WASH_OBJECT_TIME",
    "ROUTINE_NEED_BRING_ITEM",
    "ROUTINE_FORGOT_ITEM_FSI",
    "ROUTINE_CAN_USE_ITEM_HERE",
    "ROUTINE_HAVE_TO_PACK_ITEM",
    "ROUTINE_NEED_CLEAN_OBJECT",
    "ROUTINE_CLEAN_OBJECT_REASON",
    "ROUTINE_PACK_ITEM_REASON",
    "ROUTINE_REMIND_BRING_ITEM",
    "ROUTINE_CANNOT_USE_ITEM_REASON",
    "ROUTINE_TIME_TAKES_CLEAN_OBJECT",
    "ROUTINE_BEFORE_LEAVE_CHECK_ITEM",
    "ROUTINE_PARENT_RULE_CLEAN_OBJECT",
    "ROUTINE_AFTER_FINISH_ACTIVITY_FSI",
}
EXPECTED_DAILY_ROUTINE_PHASE4C_PATTERN_LEVELS = {
    ("ROUTINE_HAVE_ITEM_FSI", "A1"),
    ("ROUTINE_CLEAN_OBJECT", "A1"),
    ("ROUTINE_BRUSH_OBJECT", "A1"),
    ("ROUTINE_WASH_OBJECT", "A1"),
    ("ROUTINE_PACK_ITEM_FSI", "A1"),
    ("ROUTINE_GET_ITEM", "A1"),
    ("ROUTINE_CLEAN_OBJECT_TIME", "A1+"),
    ("ROUTINE_PACK_ITEM_TIME", "A1+"),
    ("ROUTINE_PUT_ON_ITEM_TIME", "A1+"),
    ("ROUTINE_WASH_OBJECT_TIME", "A1+"),
    ("ROUTINE_NEED_BRING_ITEM", "A2"),
    ("ROUTINE_FORGOT_ITEM_FSI", "A2"),
    ("ROUTINE_CAN_USE_ITEM_HERE", "A2"),
    ("ROUTINE_HAVE_TO_PACK_ITEM", "A2"),
    ("ROUTINE_NEED_CLEAN_OBJECT", "A2"),
    ("ROUTINE_CLEAN_OBJECT_REASON", "A2+"),
    ("ROUTINE_PACK_ITEM_REASON", "A2+"),
    ("ROUTINE_REMIND_BRING_ITEM", "A2+"),
    ("ROUTINE_CANNOT_USE_ITEM_REASON", "A2+"),
    ("ROUTINE_TIME_TAKES_CLEAN_OBJECT", "B1"),
    ("ROUTINE_BEFORE_LEAVE_CHECK_ITEM", "B1"),
    ("ROUTINE_PARENT_RULE_CLEAN_OBJECT", "B1"),
    ("ROUTINE_AFTER_FINISH_ACTIVITY_FSI", "B1"),
}
DAILY_ROUTINE_PHASE4C_MINIMUM_COUNTS = {
    "ROUTINE_HAVE_ITEM_FSI": 8,
    "ROUTINE_CLEAN_OBJECT": 4,
    "ROUTINE_BRUSH_OBJECT": 2,
    "ROUTINE_WASH_OBJECT": 2,
    "ROUTINE_PACK_ITEM_FSI": 8,
    "ROUTINE_GET_ITEM": 8,
    "ROUTINE_CLEAN_OBJECT_TIME": 5,
    "ROUTINE_PACK_ITEM_TIME": 7,
    "ROUTINE_PUT_ON_ITEM_TIME": 4,
    "ROUTINE_WASH_OBJECT_TIME": 2,
    "ROUTINE_NEED_BRING_ITEM": 10,
    "ROUTINE_FORGOT_ITEM_FSI": 4,
    "ROUTINE_CAN_USE_ITEM_HERE": 6,
    "ROUTINE_HAVE_TO_PACK_ITEM": 8,
    "ROUTINE_NEED_CLEAN_OBJECT": 5,
    "ROUTINE_CLEAN_OBJECT_REASON": 5,
    "ROUTINE_PACK_ITEM_REASON": 8,
    "ROUTINE_REMIND_BRING_ITEM": 9,
    "ROUTINE_CANNOT_USE_ITEM_REASON": 5,
    "ROUTINE_TIME_TAKES_CLEAN_OBJECT": 5,
    "ROUTINE_BEFORE_LEAVE_CHECK_ITEM": 7,
    "ROUTINE_PARENT_RULE_CLEAN_OBJECT": 5,
    "ROUTINE_AFTER_FINISH_ACTIVITY_FSI": 6,
}
EXPECTED_DAILY_ROUTINE_PHASE5_PATTERNS = {
    "ROUTINE_CLEAN_OBJECT_AGREEMENT",
    "ROUTINE_HAVE_ITEM_AGREEMENT",
    "ROUTINE_DO_DOES_QUESTION_AGREEMENT",
    "ROUTINE_NEGATIVE_AGREEMENT",
}
DAILY_ROUTINE_PHASE5_CLEAN_AGREEMENT_POSITIVE_SENTENCES = {
    "You clean your room.",
    "He cleans his room.",
    "She cleans her room.",
    "We clean our rooms.",
    "They clean their rooms.",
}
DAILY_ROUTINE_PHASE5_HAVE_AGREEMENT_POSITIVE_SENTENCES = {
    "You have your book.",
    "He has his book.",
    "She has her book.",
    "We have our books.",
    "They have their books.",
}
DAILY_ROUTINE_PHASE5_QUESTION_AGREEMENT_POSITIVE_SENTENCES = {
    "Do you clean your room?",
    "Does he clean his room?",
    "Does she clean her room?",
    "Do they clean their rooms?",
}
DAILY_ROUTINE_PHASE5_NEGATIVE_AGREEMENT_POSITIVE_SENTENCES = {
    "I do not clean my room.",
    "You do not clean your room.",
    "He does not clean his room.",
    "She does not clean her room.",
    "We do not clean our rooms.",
    "They do not clean their rooms.",
}
DAILY_ROUTINE_PHASE5_FORBIDDEN_POSITIVE_SENTENCES = {
    "She brushes her teeth.",
    "They pack their bags.",
    "Does he have his book?",
    "Does she have her book?",
    "Do they have their books?",
    "I do not have my book.",
    "You do not have your book.",
    "He does not have his book.",
    "She does not have her book.",
    "We do not have our books.",
    "They do not have their books.",
}
DAILY_ROUTINE_INVALID_AGREEMENT_SENTENCES = {
    "He clean his room.",
    "She clean her room.",
    "She cleans his room.",
    "He cleans her room.",
    "They cleans their rooms.",
    "They cleans their room.",
    "We cleans our rooms.",
    "We has our books.",
    "We has our book.",
    "He have his book.",
    "She have her book.",
    "They has their books.",
    "They has their book.",
    "He has her book.",
    "She has his book.",
    "They have his book.",
    "We have their books.",
    "Does he cleans his room?",
    "Do she clean her room?",
    "Does they clean their rooms?",
    "Does he has his book?",
    "Do she have her book?",
    "Does they have their books?",
    "He do not clean his room.",
    "She do not clean her room.",
    "They does not clean their rooms.",
    "We does not clean our rooms.",
    "He does not cleans his room.",
    "She does not cleans her room.",
    "They do not cleans their rooms.",
    "We do not cleans our rooms.",
    "He does not clean her room.",
    "She does not clean his room.",
    "They do not clean his room.",
    "We do not clean their rooms.",
    "I don't clean my room.",
    "You don't clean your room.",
    "He doesn't clean his room.",
    "She doesn't clean her room.",
    "They don't clean their rooms.",
    "We don't clean our rooms.",
}
DAILY_ROUTINE_FREE_TRANSFORMATION_SENTENCES = {
    "Do I clean my room?",
    "Did I clean my room?",
    "I cleaned my room yesterday.",
    "Yesterday, I cleaned my room.",
    "I have cleaned my room.",
    "I am cleaning my room.",
}
DAILY_ROUTINE_A1_PHASE5_BLOCKED_FRAGMENTS = {
    "He cleans",
    "She cleans",
    "They clean",
    "We clean",
    "You clean",
    "You have",
    "He has",
    "She has",
    "We have",
    "They have",
    "Does he",
    "Does she",
    "Do they",
    "Do you",
    "do not",
    "does not",
    "yesterday",
    "cleaned",
    "has his",
    "has her",
}
DAILY_ROUTINE_FORBIDDEN_PHASE5_PATTERN_IDS = {
    "ROUTINE_PACK_ITEM_AGREEMENT",
    "ROUTINE_BRUSH_OBJECT_AGREEMENT",
    "ROUTINE_WASH_OBJECT_AGREEMENT",
}


def load_banks():
    return (
        json.loads(PATTERN_BANK_PATH.read_text(encoding="utf-8")),
        json.loads(SLOT_BANK_PATH.read_text(encoding="utf-8")),
    )


def load_food_banks():
    return (
        json.loads(FOOD_PATTERN_BANK_PATH.read_text(encoding="utf-8")),
        json.loads(FOOD_SLOT_BANK_PATH.read_text(encoding="utf-8")),
    )


def load_daily_routine_sentences():
    assert DAILY_ROUTINE_SENTENCE_BANK_PATH.exists(), (
        f"Missing generated file: {DAILY_ROUTINE_SENTENCE_BANK_PATH}"
    )
    data = json.loads(DAILY_ROUTINE_SENTENCE_BANK_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def get_daily_routine_targets(sentences=None):
    if sentences is None:
        sentences = load_daily_routine_sentences()
    return {sentence["target_sentence"] for sentence in sentences}


def get_daily_routine_pattern_ids(sentences=None):
    if sentences is None:
        sentences = load_daily_routine_sentences()
    return {sentence["pattern_id"] for sentence in sentences}


def get_daily_routine_targets_for_level(level):
    return {
        sentence["target_sentence"]
        for sentence in load_daily_routine_sentences()
        if sentence["level"] == level
    }


def make_generator(seed=7, ensure_unique_targets=False):
    pattern_bank, slot_bank = load_banks()
    return ContentGenerator(
        pattern_bank=pattern_bank,
        slot_bank=slot_bank,
        rng=random.Random(seed),
        ensure_unique_targets=ensure_unique_targets,
    )


def make_food_generator(seed=7, ensure_unique_targets=False):
    pattern_bank, slot_bank = load_food_banks()
    return ContentGenerator(
        pattern_bank=pattern_bank,
        slot_bank=slot_bank,
        rng=random.Random(seed),
        ensure_unique_targets=ensure_unique_targets,
        scenario="food_drink",
        sentence_prefix="FOOD_DRINK",
    )


def make_frame_aware_generator(pattern_bank, slot_bank, seed=7, ensure_unique_targets=True):
    return ContentGenerator(
        pattern_bank=pattern_bank,
        slot_bank=slot_bank,
        rng=random.Random(seed),
        ensure_unique_targets=ensure_unique_targets,
        scenario="daily_routine",
        sentence_prefix="DAILY_ROUTINE",
    )


def make_minimal_frame_aware_banks():
    pattern_bank = {
        "TEST_EAT_FRAME": {
            "pattern_id": "TEST_EAT_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I eat {object}.",
                    "chunks_template": ["I eat", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "eat",
                    "slot_bindings": {"object": "frame_test_food_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_DO_FRAME": {
            "pattern_id": "TEST_DO_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I do {task}.",
                    "chunks_template": ["I do", "{task}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "do",
                    "slot_bindings": {"task": "frame_test_task_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_READ_FRAME": {
            "pattern_id": "TEST_READ_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I read {object}.",
                    "chunks_template": ["I read", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "read",
                    "slot_bindings": {"object": "frame_test_read_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_WATCH_FRAME": {
            "pattern_id": "TEST_WATCH_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I watch {object}.",
                    "chunks_template": ["I watch", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "watch",
                    "slot_bindings": {"object": "frame_test_watch_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_TAKE_FRAME": {
            "pattern_id": "TEST_TAKE_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I take {object}.",
                    "chunks_template": ["I take", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "take",
                    "slot_bindings": {"object": "frame_test_take_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_SCENARIO_FRAME": {
            "pattern_id": "TEST_SCENARIO_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I eat {object}.",
                    "chunks_template": ["I eat", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "eat",
                    "slot_bindings": {"object": "frame_test_scenario_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
        "TEST_BLACKLIST_FRAME": {
            "pattern_id": "TEST_BLACKLIST_FRAME",
            "variants": {
                "A1": {
                    "example_template": "I watch {object}.",
                    "chunks_template": ["I watch", "{object}"],
                    "grammar_focus": ["simple_present_affirmative"],
                    "frame": "watch",
                    "slot_bindings": {"object": "frame_test_blacklist_objects"},
                    "fsi_rules": [],
                    "complexity": {"depth": 1},
                }
            },
        },
    }
    slot_bank = {
        "frame_test_food_objects": [
            {
                "text": "breakfast",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat", "have"],
            },
            {
                "text": "lunch",
                "level": "A2",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat", "have"],
            },
            {
                "text": "homework",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "task",
                "allowed_frames": ["do"],
            },
        ],
        "frame_test_task_objects": [
            {
                "text": "homework",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "task",
                "allowed_frames": ["do"],
            }
        ],
        "frame_test_read_objects": [
            {
                "text": "a book",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "reading_object",
                "allowed_frames": ["read"],
            },
            {
                "text": "dinner",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat", "have"],
            },
        ],
        "frame_test_watch_objects": [
            {
                "text": "TV",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "media_object",
                "allowed_frames": ["watch"],
            },
            {
                "text": "breakfast",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat", "have"],
            },
        ],
        "frame_test_take_objects": [
            {
                "text": "breakfast",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat", "have"],
            }
        ],
        "frame_test_scenario_objects": [
            {
                "text": "breakfast",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["eat"],
            },
            {
                "text": "shared snack",
                "level": "A1",
                "scenario": "shared",
                "semantic_group": "food",
                "allowed_frames": ["eat"],
            },
            {
                "text": "restaurant lunch",
                "level": "A1",
                "scenario": "food_drink",
                "semantic_group": "food",
                "allowed_frames": ["eat"],
            },
        ],
        "frame_test_blacklist_objects": [
            {
                "text": "breakfast",
                "level": "A1",
                "scenario": "daily_routine",
                "semantic_group": "food",
                "allowed_frames": ["watch"],
            }
        ],
        "daily_routine_bad_phrase_blacklist": [
            "watch breakfast",
            "take breakfast",
        ],
    }
    return pattern_bank, slot_bank


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
    pattern_bank, _ = load_banks()
    by_pattern = {}
    for sentence in sentences:
        by_pattern.setdefault(sentence["pattern_id"], set()).add(sentence["level"])

    assert all(
        by_pattern[pattern_id] == set(pattern_bank[pattern_id]["variants"].keys())
        for pattern_id in EXPECTED_PATTERNS
    )


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
    for level in generator.pattern_bank["SHOP_PRICE"]["variants"].keys():
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


def test_frame_aware_generation_allows_valid_allowed_frames():
    pattern_bank, slot_bank = make_minimal_frame_aware_banks()
    generator = make_frame_aware_generator(pattern_bank, slot_bank)

    eat_sentences = generator.generate_for_pattern("TEST_EAT_FRAME", "A1", count=10)
    do_sentences = generator.generate_for_pattern("TEST_DO_FRAME", "A1", count=10)
    read_sentences = generator.generate_for_pattern("TEST_READ_FRAME", "A1", count=10)
    watch_sentences = generator.generate_for_pattern("TEST_WATCH_FRAME", "A1", count=10)

    assert {sentence["target_sentence"] for sentence in eat_sentences} == {
        "I eat breakfast."
    }
    assert {sentence["target_sentence"] for sentence in do_sentences} == {
        "I do homework."
    }
    assert {sentence["target_sentence"] for sentence in read_sentences} == {
        "I read a book."
    }
    assert {sentence["target_sentence"] for sentence in watch_sentences} == {
        "I watch TV."
    }


def test_frame_aware_generation_blocks_invalid_allowed_frames():
    pattern_bank, slot_bank = make_minimal_frame_aware_banks()
    generator = make_frame_aware_generator(pattern_bank, slot_bank)

    eat_sentences = generator.generate_for_pattern("TEST_EAT_FRAME", "A1", count=10)
    read_sentences = generator.generate_for_pattern("TEST_READ_FRAME", "A1", count=10)
    watch_sentences = generator.generate_for_pattern("TEST_WATCH_FRAME", "A1", count=10)
    take_sentences = generator.generate_for_pattern("TEST_TAKE_FRAME", "A1", count=10)

    eat_targets = {sentence["target_sentence"] for sentence in eat_sentences}
    read_targets = {sentence["target_sentence"] for sentence in read_sentences}
    watch_targets = {sentence["target_sentence"] for sentence in watch_sentences}

    assert "I eat homework." not in eat_targets
    assert "I read dinner." not in read_targets
    assert "I watch breakfast." not in watch_targets
    assert take_sentences == []


def test_frame_aware_generation_applies_level_and_scenario_filters():
    pattern_bank, slot_bank = make_minimal_frame_aware_banks()
    eat_generator = make_frame_aware_generator(pattern_bank, slot_bank)
    scenario_generator = make_frame_aware_generator(pattern_bank, slot_bank)

    eat_sentences = eat_generator.generate_for_pattern("TEST_EAT_FRAME", "A1", count=10)
    scenario_sentences = scenario_generator.generate_for_pattern(
        "TEST_SCENARIO_FRAME", "A1", count=10
    )

    eat_targets = {sentence["target_sentence"] for sentence in eat_sentences}
    scenario_targets = {sentence["target_sentence"] for sentence in scenario_sentences}

    assert "I eat lunch." not in eat_targets
    assert scenario_targets == {"I eat breakfast.", "I eat shared snack."}
    assert "I eat restaurant lunch." not in scenario_targets


def test_frame_aware_generation_applies_daily_routine_blacklist():
    pattern_bank, slot_bank = make_minimal_frame_aware_banks()
    generator = make_frame_aware_generator(pattern_bank, slot_bank)

    sentences = generator.generate_for_pattern("TEST_BLACKLIST_FRAME", "A1", count=10)

    assert sentences == []


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

    expected_total = 0
    for pattern_id in EXPECTED_PATTERNS:
        variants = generator.pattern_bank[pattern_id]["variants"]
        for level in variants.keys():
            variant = variants[level]
            requested_count = COUNT_BY_PATTERN_LEVEL.get(
                (pattern_id, level), DEFAULT_COUNT_PER_VARIANT
            )
            available_count = len(generator._enumerate_unique_candidates(variant, level))
            expected_total += min(requested_count, available_count)

    assert len(sentences) == expected_total
    assert len(ids) == len(set(ids))
    assert len(targets) == len(set(targets))


def test_each_pattern_has_a2_plus_variant():
    pattern_bank, _ = load_banks()

    assert all("A2+" in pattern_bank[pattern_id]["variants"] for pattern_id in CORE_PATTERNS)


def test_b1_patterns_have_b1_variant():
    pattern_bank, _ = load_banks()

    assert all("B1" in pattern_bank[pattern_id]["variants"] for pattern_id in B1_PATTERNS)


def test_a2_plus_generated_sentences_are_not_empty():
    generator = make_generator(seed=31, ensure_unique_targets=True)

    sentences = []
    for pattern_id in CORE_PATTERNS:
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
    assert counts[("SHOP_TOO", "A2")] == 18
    assert counts[("SHOP_TAKE", "A2")] == 15
    assert counts[("SHOP_PAY", "A2")] == 16
    assert counts[("SHOP_WANT", "A2+")] == 18
    assert counts[("SHOP_LIKE", "A2+")] == 18
    assert counts[("SHOP_TRY", "A2+")] == 18
    assert counts[("SHOP_TOO", "A2+")] == 18
    assert counts[("SHOP_PAY", "A2+")] == 16
    assert counts[("SHOP_TAKE", "A2+")] == 15
    assert counts[("SHOP_SIZE_HAVE", "A2")] == 15
    assert counts[("SHOP_SIZE_TRY", "A2")] == 5
    assert counts[("SHOP_SALE", "A2")] == 15
    assert counts[("SHOP_RECEIPT", "A2")] == 5
    assert counts[("SHOP_CHEAPER", "A2")] == 1
    assert counts[("SHOP_CHEAPEST", "A2")] == 1
    assert counts[("SHOP_COMPARE", "A2+")] == 8
    assert counts[("SHOP_ANOTHER_COLOR", "A2+")] == 14
    assert counts[("SHOP_RECOMMEND", "A2+")] == 6
    assert counts[("SHOP_LOOKS_BETTER", "A2+")] == 1
    assert counts[("SHOP_RETURN", "B1")] == 12
    assert counts[("SHOP_EXCHANGE_SIZE", "B1")] == 10
    assert counts[("SHOP_REFUND", "B1")] == 1
    assert counts[("SHOP_DAMAGE", "B1")] == 12
    assert counts[("SHOP_DAMAGE_RETURN", "B1")] == 10
    assert counts[("SHOP_RECEIPT_REFUND", "B1")] == 1
    assert counts[("SHOP_WARRANTY", "B1")] == 5
    assert counts[("SHOP_QUALITY", "B1")] == 10
    assert counts[("SHOP_MATERIAL", "B1")] == 10
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


def test_shop_too_a2_uses_paired_object_adjective_combinations():
    generator = make_generator(seed=71, ensure_unique_targets=True)
    valid_targets = {
        f"I think {item['object']} is too {item['adjective']}."
        for item in generator.slot_bank["too_item_adjective_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_TOO", "A2", count=18)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets


def test_shop_take_a2_only_uses_school_items():
    generator = make_generator(seed=73)
    school_items = {item["text"] for item in generator.slot_bank["school_items_single"]}

    sentences = generator.generate_for_pattern("SHOP_TAKE", "A2", count=15)

    assert sentences
    for sentence in sentences:
        matched_object = next(item for item in school_items if item in sentence["target_sentence"])
        assert matched_object in school_items


def test_shop_pay_a2_uses_with_and_payment_locations():
    generator = make_generator(seed=79)
    payment_locations = {item["text"] for item in generator.slot_bank["payment_locations"]}

    sentences = generator.generate_for_pattern("SHOP_PAY", "A2", count=16)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"].startswith("Can I pay with ")
        assert "Can I pay by " not in sentence["target_sentence"]
        matched_location = next(location for location in payment_locations if location in sentence["target_sentence"])
        assert matched_location in payment_locations


def test_shop_want_a2_plus_uses_positive_reason_pairs():
    generator = make_generator(seed=83, ensure_unique_targets=True)
    valid_targets = {
        f"I want {item['object']} because it is {item['reason']}."
        for item in generator.slot_bank["positive_reason_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_WANT", "A2+", count=18)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets
        assert "these " not in sentence["target_sentence"]


def test_shop_like_a2_plus_uses_positive_look_adjectives():
    generator = make_generator(seed=89)
    allowed_adjectives = {item["text"] for item in generator.slot_bank["positive_look_adjectives"]}

    sentences = generator.generate_for_pattern("SHOP_LIKE", "A2+", count=18)

    assert sentences
    for sentence in sentences:
        assert " because it looks " in sentence["target_sentence"]
        adjective = sentence["target_sentence"].rsplit(" ", 1)[-1].rstrip(".")
        assert adjective in allowed_adjectives


def test_shop_try_a2_plus_only_uses_singular_wearable_items():
    generator = make_generator(seed=97)
    singular_items = {item["text"] for item in generator.slot_bank["singular_wearable_items"]}

    sentences = generator.generate_for_pattern("SHOP_TRY", "A2+", count=18)

    assert sentences
    for sentence in sentences:
        matched_object = next(item for item in singular_items if item in sentence["target_sentence"])
        assert matched_object in singular_items
        assert "these " not in sentence["target_sentence"]


def test_shop_too_a2_plus_uses_capitalized_paired_targets():
    generator = make_generator(seed=101, ensure_unique_targets=True)
    valid_targets = {
        f"{item['subject']} is too {item['adjective']} for me."
        for item in generator.slot_bank["too_item_adjective_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_TOO", "A2+", count=18)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets
        assert sentence["target_sentence"].startswith("This ")


def test_shop_take_a2_plus_only_uses_needed_items():
    generator = make_generator(seed=127)
    needed_items = {item["text"] for item in generator.slot_bank["needed_items_single"]}

    sentences = generator.generate_for_pattern("SHOP_TAKE", "A2+", count=15)

    assert sentences
    for sentence in sentences:
        matched_object = next(item for item in needed_items if item in sentence["target_sentence"])
        assert matched_object in needed_items
        assert "this card because I need it" not in sentence["target_sentence"]
        assert "the blue one because I need it" not in sentence["target_sentence"]
        assert "this toy because I need it" not in sentence["target_sentence"]
        assert "this gift box because I need it" not in sentence["target_sentence"]


def test_shop_size_have_a2_uses_singular_clothing_and_size_options():
    generator = make_generator(seed=103)
    clothing_items = {
        item["text"]
        for item in generator.slot_bank["clothing_size_items"]
        if item["plural"] is False
    }
    size_options = {item["text"] for item in generator.slot_bank["size_options"]}

    sentences = generator.generate_for_pattern("SHOP_SIZE_HAVE", "A2", count=15)

    assert sentences
    for sentence in sentences:
        matched_object = next(item for item in clothing_items if item in sentence["target_sentence"])
        matched_size = next(size for size in size_options if f" in {size}?" in sentence["target_sentence"])
        assert matched_object in clothing_items
        assert matched_size in size_options


def test_shop_damage_b1_uses_damaged_item_pairs():
    generator = make_generator(seed=107, ensure_unique_targets=True)
    valid_targets = {
        f"{item['subject']} {item['issue']}."
        for item in generator.slot_bank["damaged_item_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_DAMAGE", "B1", count=12)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets
        assert sentence["target_sentence"][0].isupper()


def test_shop_damage_return_b1_uses_damaged_item_pairs():
    generator = make_generator(seed=109, ensure_unique_targets=True)
    valid_targets = {
        f"I'd like to return {item['object']} because it {item['issue']}."
        for item in generator.slot_bank["damaged_item_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_DAMAGE_RETURN", "B1", count=10)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets


def test_shop_material_b1_uses_material_item_pairs():
    generator = make_generator(seed=113, ensure_unique_targets=True)
    valid_targets = {
        f"Is {item['object']} made of {item['material']}?"
        for item in generator.slot_bank["material_item_pairs"]
    }

    sentences = generator.generate_for_pattern("SHOP_MATERIAL", "B1", count=10)

    assert sentences
    for sentence in sentences:
        assert sentence["target_sentence"] in valid_targets


def test_sentence_ids_are_unique_and_output_loads_into_sentence_engine():
    generator = make_generator(seed=29, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)
    ids = [sentence["sentence_id"] for sentence in sentences]

    engine = SentenceEngine(sentences)
    payload = engine.get_question_payload(ids[0], "original")

    assert len(ids) == len(set(ids))
    assert payload["sentence_id"] == ids[0]


def test_food_generated_sentences_use_food_drink_scenario_and_prefix():
    generator = make_food_generator(seed=131)

    sentence = generator.generate_for_pattern("FOOD_WANT_COUNTABLE", "A1", count=1)[0]

    assert sentence["scenario"] == "food_drink"
    assert sentence["sentence_id"].startswith("A1_FOOD_DRINK_FOOD_WANT_COUNTABLE_")


def test_food_pattern_coverage_in_generated_bank():
    generator = make_food_generator(seed=137, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=5)

    assert {sentence["pattern_id"] for sentence in sentences} == EXPECTED_FOOD_PATTERNS


def test_food_generate_all_uses_pattern_specific_counts():
    generator = make_food_generator(seed=139, ensure_unique_targets=True)

    sentences = generator.generate_all(count_per_variant=DEFAULT_COUNT_PER_VARIANT)
    counts = {}
    for sentence in sentences:
        counts[(sentence["pattern_id"], sentence["level"])] = (
            counts.get((sentence["pattern_id"], sentence["level"]), 0) + 1
        )

    assert counts[("FOOD_WANT_COUNTABLE", "A1")] == 10
    assert counts[("FOOD_WANT_UNCOUNTABLE", "A1")] == 15
    assert counts[("FOOD_CHOICE", "A1")] == 4
    assert counts[("FOOD_MEASURE_WANT", "A1")] == 6
    assert counts[("FOOD_MEASURE_HAVE", "A1")] == 6
    assert counts[("FOOD_LIKE", "A1")] == 18
    assert counts[("FOOD_HAVE", "A1")] == 20
    assert counts[("FOOD_STATE", "A1")] == 3
    assert counts[("FOOD_TOO", "A1")] == 8
    assert counts[("FOOD_EAT", "A1+")] == 15
    assert counts[("FOOD_ASK_WANT", "A1+")] == 1
    assert counts[("FOOD_DONT_WANT", "A1+")] == 12
    assert counts[("FOOD_SNACK", "A1+")] == 5
    assert counts[("FOOD_TO_GO", "A2")] == 6
    assert counts[("FOOD_WHERE_ITEM", "A2")] == 8
    assert counts[("FOOD_RECOMMEND", "A2+")] == 1
    assert counts[("FOOD_SUBSTITUTE", "A2+")] == 5
    assert counts[("FOOD_PREFER_MORE", "A2+")] == 5
    assert counts[("FOOD_RESERVATION", "B1")] == 4
    assert counts[("FOOD_CHECK", "B1")] == 1
    assert counts[("FOOD_PAY_SEPARATELY", "B1")] == 1


def test_food_too_patterns_use_food_problem_pairs():
    generator = make_food_generator(seed=149, ensure_unique_targets=True)
    valid_targets_a1 = {
        f"{item['subject']} is {item['problem']}."
        for item in generator.slot_bank["food_problem_pairs"]
    }
    valid_targets_a2 = {
        f"I think {item['item']} is {item['problem']}."
        for item in generator.slot_bank["food_problem_pairs"]
    }

    a1_sentences = generator.generate_for_pattern("FOOD_TOO", "A1", count=8)
    a2_sentences = generator.generate_for_pattern("FOOD_TOO", "A2", count=8)

    assert a1_sentences
    assert a2_sentences
    assert all(sentence["target_sentence"] in valid_targets_a1 for sentence in a1_sentences)
    assert all(sentence["target_sentence"] in valid_targets_a2 for sentence in a2_sentences)


def test_food_substitute_uses_substitution_pairs():
    generator = make_food_generator(seed=151, ensure_unique_targets=True)
    valid_targets = {
        f"Can I have {item['item_a']} instead of {item['item_b']}?"
        for item in generator.slot_bank["substitution_pairs"]
    }

    sentences = generator.generate_for_pattern("FOOD_SUBSTITUTE", "A2+", count=5)

    assert sentences
    assert all(sentence["target_sentence"] in valid_targets for sentence in sentences)


def test_food_problem_b1_uses_restaurant_problem_pairs():
    generator = make_food_generator(seed=157, ensure_unique_targets=True)
    valid_targets = {
        f"{item['subject']} {item['problem']}."
        for item in generator.slot_bank["restaurant_problem_pairs"]
    }

    sentences = generator.generate_for_pattern("FOOD_PROBLEM", "B1", count=7)

    assert sentences
    assert all(sentence["target_sentence"] in valid_targets for sentence in sentences)
    assert all(sentence["target_sentence"][0].isupper() for sentence in sentences)


def test_food_state_a1_includes_full_statement():
    generator = make_food_generator(seed=163, ensure_unique_targets=True)

    sentences = generator.generate_for_pattern("FOOD_STATE", "A1", count=3)
    targets = {sentence["target_sentence"] for sentence in sentences}

    assert "I am full." in targets


def test_food_request_a2_can_use_chopsticks():
    generator = make_food_generator(seed=167, ensure_unique_targets=True)

    sentences = generator.generate_for_pattern("FOOD_REQUEST", "A2", count=20)

    assert any("chopsticks" in sentence["target_sentence"] for sentence in sentences)


def test_food_prefer_more_a2_plus_uses_simple_drink_preference_pairs():
    generator = make_food_generator(seed=173, ensure_unique_targets=True)
    valid_targets = {
        f"I like {item['item_a']} more than {item['item_b']}."
        for item in generator.slot_bank["simple_drink_preference_pairs"]
    }

    sentences = generator.generate_for_pattern("FOOD_PREFER_MORE", "A2+", count=5)

    assert sentences
    assert all(sentence["target_sentence"] in valid_targets for sentence in sentences)


def test_daily_routine_phase4b_expected_patterns_exist():
    sentences = load_daily_routine_sentences()
    actual_patterns = {
        sentence["pattern_id"]
        for sentence in sentences
        if sentence.get("scenario") == "daily_routine"
    }

    missing = EXPECTED_DAILY_ROUTINE_PHASE4B_PATTERNS - actual_patterns
    assert not missing, f"Missing Daily Routine Phase 4B patterns: {sorted(missing)}"


def test_daily_routine_phase4c_expected_patterns_exist():
    sentences = load_daily_routine_sentences()
    pattern_ids = {sentence["pattern_id"] for sentence in sentences}

    missing = EXPECTED_DAILY_ROUTINE_PHASE4C_PATTERNS - pattern_ids
    assert not missing, f"Missing Daily Routine Phase 4C patterns: {sorted(missing)}"


def test_daily_routine_phase4c_level_coverage():
    sentences = load_daily_routine_sentences()
    pattern_levels = {
        (sentence["pattern_id"], sentence["level"])
        for sentence in sentences
    }

    missing = EXPECTED_DAILY_ROUTINE_PHASE4C_PATTERN_LEVELS - pattern_levels
    assert not missing, f"Missing Daily Routine Phase 4C pattern levels: {sorted(missing)}"


def test_daily_routine_phase4c_count_floor():
    sentences = load_daily_routine_sentences()
    counts = {}

    for sentence in sentences:
        pattern_id = sentence["pattern_id"]
        counts[pattern_id] = counts.get(pattern_id, 0) + 1

    too_low = {
        pattern_id: (counts.get(pattern_id, 0), minimum)
        for pattern_id, minimum in DAILY_ROUTINE_PHASE4C_MINIMUM_COUNTS.items()
        if counts.get(pattern_id, 0) < minimum
    }

    assert not too_low, f"Daily Routine Phase 4C counts below floor: {too_low}"


def test_daily_routine_phase4c_semantic_cleanup_regressions():
    sentences = load_daily_routine_sentences()
    texts = {sentence["target_sentence"] for sentence in sentences}

    forbidden_sentences = {
        "Can I use the chair here?",
        "Can I use the desk here?",
        "I cannot use my game now because I need to go to bed.",
        "Before I leave home, I check my shoes.",
        "I clean my study space after homework.",
        "I put on my backpack before school.",
    }

    assert texts.isdisjoint(forbidden_sentences)


def test_daily_routine_phase4c_no_unsafe_verb_object_combinations():
    sentences = load_daily_routine_sentences()
    texts = {sentence["target_sentence"] for sentence in sentences}

    forbidden_fragments = {
        "I brush my room",
        "I brush my bag",
        "I brush the table",
        "I clean my homework",
        "I clean my lunch",
        "I clean my teeth",
        "I wash my book",
        "I wash my homework",
        "I wash my pencil case",
        "I use my game",
    }

    offenders = [
        text
        for text in texts
        for fragment in forbidden_fragments
        if fragment in text
    ]

    assert not offenders, f"Unsafe verb-object combinations found: {offenders}"


def test_daily_routine_phase4c_fsi_density_examples():
    sentences = load_daily_routine_sentences()
    texts = {sentence["target_sentence"] for sentence in sentences}

    expected_examples = {
        "I have my book.",
        "I have my bag.",
        "I have my lunch.",
        "I have my homework.",
        "I clean my room.",
        "I clean my desk.",
        "I clean the table.",
        "I brush my teeth.",
        "I brush my hair.",
        "I wash my hands.",
        "I wash my face.",
        "I need to bring my homework.",
        "I need to bring my book.",
        "I forgot my book.",
        "Can I use the computer here?",
        "Please remind me to bring my book.",
        "Before I leave home, I check my bag.",
        "I clean my room because it is messy.",
        "It takes ten minutes to clean my room.",
    }

    missing = expected_examples - texts
    assert not missing, f"Missing Daily Routine Phase 4C density examples: {sorted(missing)}"


def test_daily_routine_phase5_not_implemented_yet():
    texts = get_daily_routine_targets()

    assert texts.isdisjoint(DAILY_ROUTINE_PHASE5_FORBIDDEN_POSITIVE_SENTENCES)


def test_daily_routine_phase5_clean_agreement_outputs_exist():
    texts = get_daily_routine_targets()

    missing = DAILY_ROUTINE_PHASE5_CLEAN_AGREEMENT_POSITIVE_SENTENCES - texts
    assert not missing, (
        "Missing Daily Routine Phase 5 clean agreement outputs: "
        f"{sorted(missing)}"
    )


def test_daily_routine_phase5_have_agreement_outputs_exist():
    texts = get_daily_routine_targets()

    missing = DAILY_ROUTINE_PHASE5_HAVE_AGREEMENT_POSITIVE_SENTENCES - texts
    assert not missing, (
        "Missing Daily Routine Phase 5 have agreement outputs: "
        f"{sorted(missing)}"
    )


def test_daily_routine_phase5_question_agreement_outputs_exist():
    texts = get_daily_routine_targets()

    missing = DAILY_ROUTINE_PHASE5_QUESTION_AGREEMENT_POSITIVE_SENTENCES - texts
    assert not missing, (
        "Missing Daily Routine Phase 5 question agreement outputs: "
        f"{sorted(missing)}"
    )


def test_daily_routine_phase5_negative_agreement_outputs_exist():
    texts = get_daily_routine_targets()

    missing = DAILY_ROUTINE_PHASE5_NEGATIVE_AGREEMENT_POSITIVE_SENTENCES - texts
    assert not missing, (
        "Missing Daily Routine Phase 5 negative agreement outputs: "
        f"{sorted(missing)}"
    )


def test_daily_routine_phase4c_generated_bank_has_all_levels():
    sentences = load_daily_routine_sentences()
    levels = {sentence["level"] for sentence in sentences}

    assert {"A1", "A1+", "A2", "A2+", "B1"}.issubset(levels)


def test_daily_routine_ready_pattern_uses_unique_sentence():
    sentences = load_daily_routine_sentences()
    ready_sentences = [
        sentence for sentence in sentences if sentence.get("pattern_id") == "ROUTINE_READY"
    ]

    assert ready_sentences
    targets = {sentence["target_sentence"] for sentence in ready_sentences}
    assert "I am ready now." in targets
    assert "I am ready." not in targets


def test_daily_routine_no_redundant_homework_reason():
    sentences = load_daily_routine_sentences()
    targets = {sentence["target_sentence"] for sentence in sentences}

    assert "I need to do my homework because I have homework." not in targets
    assert "I need to do my homework because it is due tomorrow." in targets


def test_daily_routine_weekday_weekend_uses_week_contexts():
    sentences = load_daily_routine_sentences()
    weekday_weekend_targets = {
        sentence["target_sentence"]
        for sentence in sentences
        if sentence.get("pattern_id") == "ROUTINE_WEEKDAY_WEEKEND"
    }

    assert "I listen to music after school." not in weekday_weekend_targets
    assert "I listen to music on weekends." in weekday_weekend_targets


def test_daily_routine_no_bad_permission_pairs():
    sentences = load_daily_routine_sentences()
    bad_phrases = [
        "Can I go to bed after homework",
        "Can I go to school after dinner",
        "Can I brush my teeth after school",
    ]

    for sentence in sentences:
        target = sentence["target_sentence"]
        assert not any(bad in target for bad in bad_phrases), target


def test_daily_routine_invalid_agreement_outputs_are_forbidden():
    texts = get_daily_routine_targets()

    assert texts.isdisjoint(DAILY_ROUTINE_INVALID_AGREEMENT_SENTENCES)


def test_daily_routine_forgot_allowed_as_fixed_expression():
    sentences = load_daily_routine_sentences()
    forgot_sentences = [
        sentence for sentence in sentences if sentence.get("pattern_id") == "ROUTINE_FORGOT"
    ]

    assert forgot_sentences
    assert all(
        sentence["target_sentence"].startswith("I forgot ")
        for sentence in forgot_sentences
    )


def test_daily_routine_has_no_free_transformation_outputs():
    texts = get_daily_routine_targets()

    assert texts.isdisjoint(DAILY_ROUTINE_FREE_TRANSFORMATION_SENTENCES)


def test_daily_routine_phase5_pattern_id_boundary():
    pattern_ids = get_daily_routine_pattern_ids()

    missing_phase5 = EXPECTED_DAILY_ROUTINE_PHASE5_PATTERNS - pattern_ids
    assert not missing_phase5, (
        f"Missing expected Phase 5 pattern IDs: {sorted(missing_phase5)}"
    )

    dr_pattern_ids = sorted(
        pattern_id for pattern_id in pattern_ids if pattern_id.startswith("DR_")
    )
    assert not dr_pattern_ids, f"Unexpected DR_* pattern IDs: {dr_pattern_ids}"

    non_routine_pattern_ids = sorted(
        pattern_id for pattern_id in pattern_ids if not pattern_id.startswith("ROUTINE_")
    )
    assert not non_routine_pattern_ids, (
        f"Unexpected non-ROUTINE_* pattern IDs: {non_routine_pattern_ids}"
    )

    missing = {
        "ROUTINE_HAVE_ITEM_FSI",
        "ROUTINE_CLEAN_OBJECT",
        "ROUTINE_BRUSH_OBJECT",
        "ROUTINE_WASH_OBJECT",
        "ROUTINE_NEED_BRING_ITEM",
        "ROUTINE_FORGOT_ITEM_FSI",
        "ROUTINE_REMIND_BRING_ITEM",
        "ROUTINE_BEFORE_LEAVE_CHECK_ITEM",
        "ROUTINE_CLEAN_OBJECT_REASON",
        "ROUTINE_PACK_ITEM_REASON",
        "ROUTINE_CANNOT_USE_ITEM_REASON",
        "ROUTINE_TIME_TAKES_CLEAN_OBJECT",
        "ROUTINE_AFTER_FINISH_ACTIVITY_FSI",
    } - pattern_ids
    assert not missing, f"Missing required ROUTINE_* pattern IDs: {sorted(missing)}"

    assert pattern_ids.isdisjoint(DAILY_ROUTINE_FORBIDDEN_PHASE5_PATTERN_IDS)


def test_daily_routine_a1_has_no_phase5_agreement_expansion():
    a1_targets = get_daily_routine_targets_for_level("A1")

    assert a1_targets
    assert all(
        fragment.lower() not in target.lower()
        for target in a1_targets
        for fragment in DAILY_ROUTINE_A1_PHASE5_BLOCKED_FRAGMENTS
    )


def test_daily_routine_phase4c_semantic_safety_examples_are_absent():
    sentences = load_daily_routine_sentences()
    texts = {sentence["target_sentence"] for sentence in sentences}

    forbidden_sentences = {
        "I clean my homework.",
        "I clean my teeth.",
        "I brush my room.",
        "I brush the table.",
        "I wash my homework.",
        "I brush my teeth because I am hungry.",
        "I drink water because I am sleepy.",
        "I pack my lunch because it is messy.",
        "He clean his room.",
        "She clean her room.",
        "She cleans his room.",
        "He cleans her room.",
        "They pack their bags.",
        "Yesterday, I cleaned my room.",
        "I cleaned my room yesterday.",
    }

    assert texts.isdisjoint(forbidden_sentences)


def test_daily_routine_phase4c_density_counts_for_core_frames():
    sentences = load_daily_routine_sentences()

    have_item_targets = {
        sentence["target_sentence"]
        for sentence in sentences
        if sentence["pattern_id"] == "ROUTINE_HAVE_ITEM_FSI"
    }
    clean_object_targets = {
        sentence["target_sentence"]
        for sentence in sentences
        if sentence["pattern_id"] == "ROUTINE_CLEAN_OBJECT"
    }
    brush_object_targets = {
        sentence["target_sentence"]
        for sentence in sentences
        if sentence["pattern_id"] == "ROUTINE_BRUSH_OBJECT"
    }

    assert len(have_item_targets) >= 8
    assert len(clean_object_targets) >= 4
    assert len(brush_object_targets) >= 2


def test_daily_routine_phase5_plan_doc_exists():
    assert DAILY_ROUTINE_PHASE5_PLAN_PATH.exists()
    assert DAILY_ROUTINE_PHASE4C_A_NOTES_PATH.exists()
    assert DAILY_ROUTINE_PHASE4C_B_NOTES_PATH.exists()


def test_daily_routine_phase4c_generated_sentence_count_remains_stable():
    sentences = load_daily_routine_sentences()
    level_counts = Counter(sentence["level"] for sentence in sentences)

    # This baseline removes the unnatural frame output "I go to home",
    # keeps "I go home" through existing routine coverage, and includes
    # the production read-object and watch-object frame trials with
    # deterministic unique-target reshuffle.
    assert len(sentences) == 811
    assert level_counts["A1"] == 137
    assert level_counts["A1+"] == 242
    assert level_counts["A2"] == 209
    assert level_counts["A2+"] == 127
    assert level_counts["B1"] == 96


def test_daily_routine_phase4b_level_and_count_coverage():
    sentences = load_daily_routine_sentences()
    levels = {sentence["level"] for sentence in sentences}
    assert {"A1", "A1+", "A2", "A2+", "B1"}.issubset(levels)

    assert len(sentences) >= 300

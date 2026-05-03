import argparse
import itertools
import json
import random
from pathlib import Path


DEFAULT_COUNT_PER_VARIANT = 30
COUNT_BY_PATTERN_LEVEL = {
    ("SHOP_TOO", "A1"): 24,
    ("SHOP_PAY", "A1"): 16,
    ("SHOP_TOO", "A1+"): 18,
    ("SHOP_PAY", "A1+"): 16,
    ("SHOP_LOOKING", "A1+"): 15,
    ("SHOP_TOO", "A2"): 18,
    ("SHOP_TAKE", "A2"): 15,
    ("SHOP_PAY", "A2"): 16,
    ("SHOP_WANT", "A2+"): 18,
    ("SHOP_LIKE", "A2+"): 18,
    ("SHOP_TRY", "A2+"): 18,
    ("SHOP_TOO", "A2+"): 18,
    ("SHOP_PAY", "A2+"): 16,
    ("SHOP_TAKE", "A2+"): 15,
    ("SHOP_SIZE_HAVE", "A2"): 15,
    ("SHOP_SIZE_TRY", "A2"): 5,
    ("SHOP_SALE", "A2"): 15,
    ("SHOP_RECEIPT", "A2"): 5,
    ("SHOP_CHEAPER", "A2"): 1,
    ("SHOP_CHEAPEST", "A2"): 1,
    ("SHOP_COMPARE", "A2+"): 8,
    ("SHOP_ANOTHER_COLOR", "A2+"): 14,
    ("SHOP_RECOMMEND", "A2+"): 6,
    ("SHOP_LOOKS_BETTER", "A2+"): 1,
    ("SHOP_RETURN", "B1"): 12,
    ("SHOP_EXCHANGE_SIZE", "B1"): 10,
    ("SHOP_REFUND", "B1"): 1,
    ("SHOP_DAMAGE", "B1"): 12,
    ("SHOP_DAMAGE_RETURN", "B1"): 10,
    ("SHOP_RECEIPT_REFUND", "B1"): 1,
    ("SHOP_WARRANTY", "B1"): 5,
    ("SHOP_QUALITY", "B1"): 10,
    ("SHOP_MATERIAL", "B1"): 10,
    ("FOOD_WANT_COUNTABLE", "A1"): 10,
    ("FOOD_WANT_UNCOUNTABLE", "A1"): 15,
    ("FOOD_CHOICE", "A1"): 4,
    ("FOOD_MEASURE_WANT", "A1"): 6,
    ("FOOD_MEASURE_HAVE", "A1"): 6,
    ("FOOD_LIKE", "A1"): 18,
    ("FOOD_HAVE", "A1"): 20,
    ("FOOD_PRICE", "A1"): 10,
    ("FOOD_STATE", "A1"): 3,
    ("FOOD_TOO", "A1"): 8,
    ("FOOD_EAT", "A1+"): 15,
    ("FOOD_ASK_WANT", "A1+"): 1,
    ("FOOD_DRINK", "A1+"): 9,
    ("FOOD_DONT_WANT", "A1+"): 12,
    ("FOOD_HAVE_POLITE", "A1+"): 20,
    ("FOOD_HAVE_STOCK", "A1+"): 18,
    ("FOOD_BREAKFAST", "A1+"): 6,
    ("FOOD_LUNCH", "A1+"): 6,
    ("FOOD_DINNER", "A1+"): 6,
    ("FOOD_SNACK", "A1+"): 5,
    ("FOOD_TO_GO", "A1+"): 6,
    ("FOOD_ORDER", "A2"): 20,
    ("FOOD_REQUEST", "A2"): 8,
    ("FOOD_ANY_HAVE", "A2"): 15,
    ("FOOD_TO_GO", "A2"): 6,
    ("FOOD_NO_ICE", "A2"): 1,
    ("FOOD_LESS_SUGAR", "A2"): 1,
    ("FOOD_RESTROOM", "A2"): 1,
    ("FOOD_WHERE_ITEM", "A2"): 8,
    ("FOOD_TOO", "A2"): 8,
    ("FOOD_LIKE_REASON", "A2+"): 10,
    ("FOOD_WANT_REASON", "A2+"): 10,
    ("FOOD_NOT_WANT_REASON", "A2+"): 6,
    ("FOOD_RECOMMEND", "A2+"): 1,
    ("FOOD_RECOMMEND_CONTEXT", "A2+"): 6,
    ("FOOD_INGREDIENT", "A2+"): 8,
    ("FOOD_SUBSTITUTE", "A2+"): 5,
    ("FOOD_PREFER_MORE", "A2+"): 5,
    ("FOOD_RESERVATION", "B1"): 4,
    ("FOOD_TABLE", "B1"): 4,
    ("FOOD_ORDER_DETAIL", "B1"): 15,
    ("FOOD_WITHOUT", "B1"): 8,
    ("FOOD_ALLERGY", "B1"): 6,
    ("FOOD_INGREDIENT_DETAIL", "B1"): 8,
    ("FOOD_VEGETARIAN_RECOMMEND", "B1"): 1,
    ("FOOD_PROBLEM", "B1"): 7,
    ("FOOD_REPLACEMENT", "B1"): 1,
    ("FOOD_CHECK", "B1"): 1,
    ("FOOD_SPLIT_CHECK", "B1"): 1,
    ("FOOD_PAY_SEPARATELY", "B1"): 1,
    ("FOOD_TO_GO", "B1"): 1,
    ("ROUTINE_DO", "A1"): 20,
    ("ROUTINE_BE_STATE", "A1"): 12,
    ("ROUTINE_PLACE", "A1"): 10,
    ("ROUTINE_DO_TIME", "A1+"): 18,
    ("ROUTINE_LIKE", "A1+"): 15,
    ("ROUTINE_WANT", "A1+"): 15,
    ("ROUTINE_BE_STATE_TODAY", "A1+"): 12,
    ("ROUTINE_NEED", "A2"): 16,
    ("ROUTINE_HAVE_TO", "A2"): 16,
    ("ROUTINE_WOULD_LIKE", "A2"): 14,
    ("ROUTINE_CAN_PLACE", "A2"): 12,
    ("ROUTINE_TOO", "A2"): 12,
    ("ROUTINE_REASON", "A2+"): 15,
    ("ROUTINE_BEFORE_AFTER", "A2+"): 15,
    ("ROUTINE_PREFERENCE_REASON", "A2+"): 12,
    ("ROUTINE_PROBLEM_REASON", "A2+"): 12,
    ("ROUTINE_USUALLY", "B1"): 16,
    ("ROUTINE_CLOCK_TIME", "B1"): 16,
    ("ROUTINE_WEEKDAY_WEEKEND", "B1"): 14,
    ("ROUTINE_CANNOT_BECAUSE", "B1"): 12,
    ("ROUTINE_FINISH_BEFORE", "B1"): 12,
    ("ROUTINE_ROUTINE_OPINION", "B1"): 12,
}

SCENARIO_CONFIGS = {
    "shopping": {
        "sentence_prefix": "SHOPPING",
        "pattern_path": Path("data/pattern_bank/shopping_patterns.json"),
        "slot_path": Path("data/slot_bank/shopping_slots.json"),
        "output_path": Path("data/generated/shopping_sentence_bank.json"),
    },
    "food_drink": {
        "sentence_prefix": "FOOD_DRINK",
        "pattern_path": Path("data/pattern_bank/food_drink_patterns.json"),
        "slot_path": Path("data/slot_bank/food_drink_slots.json"),
        "output_path": Path("data/generated/food_drink_sentence_bank.json"),
    },
    "daily_routine": {
        "sentence_prefix": "DAILY_ROUTINE",
        "pattern_path": Path("data/pattern_bank/daily_routine_patterns.json"),
        "slot_path": Path("data/slot_bank/daily_routine_slots.json"),
        "output_path": Path("data/generated/daily_routine_sentence_bank.json"),
    },
}


class ContentGenerator:
    REQUIRED_FIELDS = [
        "sentence_id",
        "level",
        "scenario",
        "pattern_id",
        "target_sentence",
        "chunks",
        "grammar_focus",
        "fsi_tasks",
    ]

    def __init__(
        self,
        pattern_bank,
        slot_bank,
        rng=None,
        ensure_unique_targets=False,
        scenario="shopping",
        sentence_prefix=None,
    ):
        self.pattern_bank = pattern_bank
        self.slot_bank = slot_bank
        self.rng = rng or random.Random()
        self.ensure_unique_targets = ensure_unique_targets
        self.scenario = scenario
        self.sentence_prefix = sentence_prefix or scenario.upper()
        self._sentence_counters = {}
        self._used_target_sentences = set()

    def generate_for_pattern(self, pattern_id, level, count=5, n=None):
        if n is not None:
            count = n
        variant = self._get_variant(pattern_id, level)
        sentence_parts = self._build_sentence_parts(variant, count)
        sentences = []

        for slot_values, target_sentence in sentence_parts:
            chunks = self._render_chunks(variant["chunks_template"], slot_values)
            sentence_index = self._next_sentence_index(pattern_id, level)
            sentence = {
                "sentence_id": f"{level}_{self.sentence_prefix}_{pattern_id}_{sentence_index:03d}",
                "level": level,
                "scenario": self.scenario,
                "pattern_id": pattern_id,
                "target_sentence": target_sentence,
                "chunks": chunks,
                "translation": "",
                "grammar_focus": list(variant["grammar_focus"]),
                "difficulty_score": variant.get("complexity", {}).get("depth", 1),
                "fsi_tasks": self._build_fsi_tasks(pattern_id, variant, slot_values),
            }
            self._validate_sentence(sentence)
            self._used_target_sentences.add(target_sentence)
            sentences.append(sentence)

        return sentences

    def generate_all(self, pattern_ids=None, levels=None, count_per_variant=5):
        pattern_ids = pattern_ids or list(self.pattern_bank.keys())
        levels = levels or self._available_levels(pattern_ids)
        sentences = []
        for level in levels:
            for pattern_id in pattern_ids:
                pattern_levels = self.pattern_bank[pattern_id].get("variants", self.pattern_bank[pattern_id]).keys()
                if level not in pattern_levels:
                    continue
                count = COUNT_BY_PATTERN_LEVEL.get((pattern_id, level), count_per_variant)
                sentences.extend(
                    self.generate_for_pattern(
                        pattern_id=pattern_id,
                        level=level,
                        count=count,
                    )
                )
        return sentences

    def _get_variant(self, pattern_id, level):
        try:
            pattern_entry = self.pattern_bank[pattern_id]
            variants = pattern_entry.get("variants", pattern_entry)
            return variants[level]
        except KeyError as exc:
            raise ValueError(f"Unknown pattern variant: {pattern_id} / {level}") from exc

    def _available_levels(self, pattern_ids):
        ordered = []
        for pattern_id in pattern_ids:
            pattern_entry = self.pattern_bank[pattern_id]
            variants = pattern_entry.get("variants", pattern_entry)
            for level in variants:
                if level not in ordered:
                    ordered.append(level)
        return ordered

    def _next_sentence_index(self, pattern_id, level):
        key = (pattern_id, level)
        current = self._sentence_counters.get(key, 0) + 1
        self._sentence_counters[key] = current
        return current

    def _resolve_slot_values(self, variant):
        slot_constraints = variant.get("slot_constraints", {})
        slot_values = dict(self._resolve_paired_slot_values(variant))
        for slot_name, constraints in slot_constraints.items():
            if slot_name in slot_values:
                continue
            candidates = self._filter_slot_candidates(constraints)
            if not candidates:
                raise ValueError(f"No slot candidates found for {slot_name}: {constraints}")
            slot_values[slot_name] = self.rng.choice(candidates)["text"]
        return slot_values

    def _build_sentence_parts(self, variant, count):
        if not self.ensure_unique_targets:
            return [self._build_random_sentence_parts(variant) for _ in range(count)]

        candidates = self._enumerate_unique_candidates(variant)
        available = [
            candidate
            for candidate in candidates
            if candidate[1] not in self._used_target_sentences
        ]
        self.rng.shuffle(available)
        return available[: min(count, len(available))]

    def _build_random_sentence_parts(self, variant):
        slot_values = self._resolve_slot_values(variant)
        template = variant.get("example_template", variant.get("template"))
        target_sentence = template.format(**slot_values)
        return slot_values, target_sentence

    def _enumerate_unique_candidates(self, variant):
        slot_constraints = variant.get("slot_constraints", {})
        template = variant.get("example_template", variant.get("template"))
        paired_candidates = self._enumerate_paired_candidates(variant, template)
        slot_names = [slot_name for slot_name in slot_constraints.keys() if not self._slot_is_paired(slot_constraints[slot_name])]
        slot_candidate_lists = []
        seed_candidates = paired_candidates or [({}, None)]

        for slot_name in slot_names:
            candidates = self._filter_slot_candidates(slot_constraints[slot_name])
            if not candidates:
                raise ValueError(f"No slot candidates found for {slot_name}: {slot_constraints[slot_name]}")
            slot_candidate_lists.append(candidates)

        unique_candidates = {}
        if not slot_candidate_lists:
            for seed_values, _ in seed_candidates:
                target_sentence = template.format(**seed_values)
                unique_candidates.setdefault(target_sentence, (seed_values, target_sentence))
            return list(unique_candidates.values())

        for seed_values, _ in seed_candidates:
            for combination in itertools.product(*slot_candidate_lists):
                slot_values = dict(seed_values)
                slot_values.update(
                    {
                        slot_name: item["text"]
                        for slot_name, item in zip(slot_names, combination)
                    }
                )
                target_sentence = template.format(**slot_values)
                unique_candidates.setdefault(target_sentence, (slot_values, target_sentence))

        return list(unique_candidates.values())

    def _resolve_paired_slot_values(self, variant):
        pair_category = self._get_pair_category(variant)
        if pair_category is None:
            return {}

        pair_items = self.slot_bank.get(pair_category, [])
        if not pair_items:
            raise ValueError(f"No paired slot candidates found for {pair_category}")

        return dict(self.rng.choice(pair_items))

    def _enumerate_paired_candidates(self, variant, template):
        pair_category = self._get_pair_category(variant)
        if pair_category is None:
            return None

        slot_constraints = variant.get("slot_constraints", {})
        paired_slot_names = [
            slot_name
            for slot_name, constraints in slot_constraints.items()
            if constraints.get("pair_category") == pair_category
        ]
        paired_groups = {
            constraints.get("pair_category")
            for constraints in slot_constraints.values()
            if constraints.get("pair_category")
        }
        if paired_groups and paired_groups != {pair_category}:
            raise ValueError(f"Paired slots must share one pair category: {paired_groups}")

        pair_items = self.slot_bank.get(pair_category, [])
        if not pair_items:
            raise ValueError(f"No paired slot candidates found for {pair_category}")

        unique_candidates = {}
        for pair_item in pair_items:
            slot_values = {}
            if paired_slot_names:
                slot_values.update(
                    {slot_name: pair_item[slot_name] for slot_name in paired_slot_names}
                )
            else:
                slot_values.update(pair_item)
            candidate_key = tuple(sorted(slot_values.items()))
            unique_candidates.setdefault(candidate_key, (slot_values, None))

        return list(unique_candidates.values())

    def _get_pair_category(self, variant):
        paired_slot = variant.get("paired_slot")
        if paired_slot:
            category = paired_slot.get("category")
            if not category:
                raise ValueError("paired_slot requires a category")
            return category

        slot_constraints = variant.get("slot_constraints", {})
        paired_groups = {
            constraints.get("pair_category")
            for constraints in slot_constraints.values()
            if constraints.get("pair_category")
        }
        if not paired_groups:
            return None
        if len(paired_groups) != 1:
            raise ValueError(f"Paired slots must share one pair category: {paired_groups}")
        return paired_groups.pop()

    def _slot_is_paired(self, constraints):
        return bool(constraints.get("pair_category"))

    def _filter_slot_candidates(self, constraints):
        groups = constraints.get("category", [])
        candidates = []

        for group_name in groups:
            group_items = self.slot_bank.get(group_name, [])
            candidates.extend(group_items)

        filtered = []
        seen = set()

        for item in candidates:
            text = item["text"]
            if text in seen:
                continue
            if self._matches_constraints(item, constraints):
                filtered.append(item)
                seen.add(text)

        return filtered

    def _matches_constraints(self, item, constraints):
        for key, expected in constraints.items():
            if key == "category":
                continue
            if item.get(key) != expected:
                return False
        return True

    def _render_chunks(self, chunks_template, slot_values):
        return [chunk.format(**slot_values) for chunk in chunks_template]

    def _build_fsi_tasks(self, pattern_id, variant, slot_values):
        tasks = []
        for rule in variant.get("fsi_rules", []):
            task = self._build_fsi_task(pattern_id, variant, rule, slot_values)
            if task is not None:
                tasks.append(task)
        return tasks

    def _build_fsi_task(self, pattern_id, variant, rule, slot_values):
        obj = slot_values.get("object", "")
        comparison_object = slot_values.get("comparison_object", "")
        adjective = slot_values.get("adjective", "")
        payment_method = slot_values.get("payment_method", "")

        if pattern_id == "SHOP_WANT":
            if rule == "negative":
                return {
                    "task_type": "negative",
                    "target": f"I do not want {obj}.",
                    "chunks": ["I do not want", obj],
                }
            if rule == "question":
                return {
                    "task_type": "question",
                    "target": f"Do you want {obj}?",
                    "chunks": ["Do you want", obj, "?"],
                }

        if pattern_id == "SHOP_LIKE":
            if rule == "negative":
                return {
                    "task_type": "negative",
                    "target": f"I do not like {obj}.",
                    "chunks": ["I do not like", obj],
                }
            if rule == "question":
                return {
                    "task_type": "question",
                    "target": f"Do you like {obj}?",
                    "chunks": ["Do you like", obj, "?"],
                }

        if pattern_id == "SHOP_TRY" and rule == "negative":
            return {
                "task_type": "negative",
                "target": f"I cannot try on {obj}.",
                "chunks": ["I cannot try on", obj],
            }

        if pattern_id == "SHOP_TAKE" and rule == "negative":
            return {
                "task_type": "negative",
                "target": f"I will not take {obj}.",
                "chunks": ["I will not take", obj],
            }

        if pattern_id == "SHOP_LOOKING" and rule == "question":
            return {
                "task_type": "question",
                "target": f"Are you looking for {obj}?",
                "chunks": ["Are you looking for", obj, "?"],
            }

        if pattern_id == "SHOP_PAY" and rule == "question" and payment_method:
            question_chunks = ["Can I pay by", payment_method, "?"]
            question_target = f"Can I pay by {payment_method}?"
            if any("with" in chunk for chunk in variant.get("chunks_template", [])):
                question_chunks = ["Can I pay with", payment_method, "?"]
                question_target = f"Can I pay with {payment_method}?"
            return {
                "task_type": "question",
                "target": question_target,
                "chunks": question_chunks,
            }

        if pattern_id == "SHOP_PRICE" and rule == "substitution":
            return None

        return None

    def _validate_sentence(self, sentence):
        missing = [field for field in self.REQUIRED_FIELDS if field not in sentence]
        if missing:
            raise ValueError(f"Sentence missing required fields: {missing}")
        if not sentence["chunks"]:
            raise ValueError("Sentence chunks cannot be empty")
        if not sentence["grammar_focus"]:
            raise ValueError("Sentence grammar_focus cannot be empty")
        return True


def _load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_scenario_bank(base_dir, scenario_name):
    config = SCENARIO_CONFIGS[scenario_name]
    pattern_path = base_dir / config["pattern_path"]
    slot_path = base_dir / config["slot_path"]
    output_path = base_dir / config["output_path"]
    generator = ContentGenerator(
        pattern_bank=_load_json(pattern_path),
        slot_bank=_load_json(slot_path),
        ensure_unique_targets=True,
        scenario=scenario_name,
        sentence_prefix=config["sentence_prefix"],
    )
    sentences = generator.generate_all(count_per_variant=DEFAULT_COUNT_PER_VARIANT)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(sentences, handle, ensure_ascii=False, indent=2)
    return output_path, len(sentences)


def main():
    parser = argparse.ArgumentParser(description="Generate sentence banks for supported scenarios.")
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIO_CONFIGS.keys()),
        help="Generate one or more specific scenarios. When omitted, only missing banks are generated.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    scenario_names = args.scenario or list(SCENARIO_CONFIGS.keys())
    missing_only = args.scenario is None

    for scenario_name in scenario_names:
        output_path = base_dir / SCENARIO_CONFIGS[scenario_name]["output_path"]
        if missing_only and output_path.exists():
            print(f"Skipped {scenario_name}: {output_path} already exists")
            continue

        generated_path, count = generate_scenario_bank(base_dir, scenario_name)
        print(f"Generated {count} sentences to {generated_path}")


if __name__ == "__main__":
    main()

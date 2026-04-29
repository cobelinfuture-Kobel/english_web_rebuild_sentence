import json
import itertools
import random
from pathlib import Path


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

    def __init__(self, pattern_bank, slot_bank, rng=None, ensure_unique_targets=False):
        self.pattern_bank = pattern_bank
        self.slot_bank = slot_bank
        self.rng = rng or random.Random()
        self.ensure_unique_targets = ensure_unique_targets
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
                "sentence_id": f"{level}_SHOPPING_{pattern_id}_{sentence_index:03d}",
                "level": level,
                "scenario": "shopping",
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
                sentences.extend(
                    self.generate_for_pattern(
                        pattern_id=pattern_id,
                        level=level,
                        count=count_per_variant,
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

    def _resolve_slot_values(self, slot_constraints):
        slot_values = {}
        for slot_name, constraints in slot_constraints.items():
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
        if len(available) < count:
            raise ValueError("Unable to generate enough unique target_sentence values for the requested variant")

        self.rng.shuffle(available)
        return available[:count]

    def _build_random_sentence_parts(self, variant):
        slot_values = self._resolve_slot_values(variant["slot_constraints"])
        template = variant.get("example_template", variant.get("template"))
        target_sentence = template.format(**slot_values)
        return slot_values, target_sentence

    def _enumerate_unique_candidates(self, variant):
        slot_constraints = variant["slot_constraints"]
        template = variant.get("example_template", variant.get("template"))
        slot_names = list(slot_constraints.keys())
        slot_candidate_lists = []

        for slot_name in slot_names:
            candidates = self._filter_slot_candidates(slot_constraints[slot_name])
            if not candidates:
                raise ValueError(f"No slot candidates found for {slot_name}: {slot_constraints[slot_name]}")
            slot_candidate_lists.append(candidates)

        unique_candidates = {}
        for combination in itertools.product(*slot_candidate_lists):
            slot_values = {
                slot_name: item["text"]
                for slot_name, item in zip(slot_names, combination)
            }
            target_sentence = template.format(**slot_values)
            unique_candidates.setdefault(target_sentence, (slot_values, target_sentence))

        return list(unique_candidates.values())

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
            task = self._build_fsi_task(pattern_id, rule, slot_values)
            if task is not None:
                tasks.append(task)
        return tasks

    def _build_fsi_task(self, pattern_id, rule, slot_values):
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
            return {
                "task_type": "question",
                "target": f"Can I pay by {payment_method}?",
                "chunks": ["Can I pay by", payment_method, "?"],
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


def main():
    base_dir = Path(__file__).resolve().parent.parent
    pattern_path = base_dir / "data" / "pattern_bank" / "shopping_patterns.json"
    slot_path = base_dir / "data" / "slot_bank" / "shopping_slots.json"
    output_path = base_dir / "data" / "generated" / "shopping_sentence_bank.json"

    generator = ContentGenerator(
        pattern_bank=_load_json(pattern_path),
        slot_bank=_load_json(slot_path),
        ensure_unique_targets=True,
    )
    sentences = generator.generate_all(count_per_variant=5)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(sentences, handle, ensure_ascii=False, indent=2)

    print(f"Generated {len(sentences)} sentences to {output_path}")


if __name__ == "__main__":
    main()

from collections import defaultdict


def _get_sentence_id(sentence):
    return sentence.get("sentence_id") or sentence.get("id") or sentence.get("target_id")


def _get_sentence_level(sentence):
    return sentence.get("level") or "UNKNOWN"


def _get_sentence_pattern(sentence):
    return sentence.get("pattern") or sentence.get("pattern_id") or "UNKNOWN"


def _build_sentence_index(sentences, *, level=None, pattern=None):
    sentence_index = {}

    for sentence in sentences:
        sentence_id = _get_sentence_id(sentence)
        if not sentence_id:
            continue

        sentence_level = _get_sentence_level(sentence)
        sentence_pattern = _get_sentence_pattern(sentence)

        if level is not None and sentence_level != level:
            continue

        if pattern is not None and sentence_pattern != pattern:
            continue

        sentence_index[sentence_id] = {
            "sentence_id": sentence_id,
            "level": sentence_level,
            "pattern": sentence_pattern,
        }

    return sentence_index


def _sort_sentence_meta(sentence_meta):
    return (
        sentence_meta["level"],
        sentence_meta["pattern"],
        sentence_meta["sentence_id"],
    )


def _build_base_response(user_id, limit, level, pattern):
    return {
        "user_id": user_id,
        "strategy": "none",
        "is_exhausted": True,
        "limit": limit,
        "filters": {
            "level": level,
            "pattern": pattern,
        },
        "recommendations": [],
    }


def _serialize_recommendations(sentence_metas, reason):
    return [
        {
            "sentence_id": sentence_meta["sentence_id"],
            "level": sentence_meta["level"],
            "pattern": sentence_meta["pattern"],
            "reason": reason,
        }
        for sentence_meta in sentence_metas
    ]


def _get_user_attempts(user_id, attempts, valid_sentence_ids):
    return [
        attempt
        for attempt in attempts
        if attempt.get("user_id") == user_id and attempt.get("sentence_id") in valid_sentence_ids
    ]


def _get_weak_patterns(user_attempts):
    by_pattern = defaultdict(list)
    for attempt in user_attempts:
        pattern = attempt.get("pattern")
        if pattern is None:
            continue
        by_pattern[pattern].append(attempt)

    weak_patterns = []
    for pattern, pattern_attempts in by_pattern.items():
        total_attempts = len(pattern_attempts)
        if total_attempts < 5:
            continue

        correct_attempts = sum(1 for attempt in pattern_attempts if attempt.get("is_correct"))
        wrong_attempts = total_attempts - correct_attempts
        accuracy = correct_attempts / total_attempts if total_attempts else 0
        if accuracy >= 0.7:
            continue

        weak_patterns.append(
            {
                "pattern": pattern,
                "total_attempts": total_attempts,
                "wrong_attempts": wrong_attempts,
                "accuracy": accuracy,
            }
        )

    return sorted(
        weak_patterns,
        key=lambda item: (item["accuracy"], -item["wrong_attempts"], item["pattern"]),
    )


def _get_not_attempted_sentence_metas(sentence_index, attempted_ids, *, pattern=None):
    sentence_metas = []
    for sentence_id, sentence_meta in sentence_index.items():
        if sentence_id in attempted_ids:
            continue
        if pattern is not None and sentence_meta["pattern"] != pattern:
            continue
        sentence_metas.append(sentence_meta)
    return sorted(sentence_metas, key=_sort_sentence_meta)


def _get_latest_wrong_attempts(user_attempts):
    latest_by_sentence = {}

    for attempt in user_attempts:
        if attempt.get("is_correct"):
            continue

        sentence_id = attempt.get("sentence_id")
        existing = latest_by_sentence.get(sentence_id)
        if existing is None:
            latest_by_sentence[sentence_id] = attempt
            continue

        current_key = (attempt.get("created_at", ""), attempt.get("id", ""))
        existing_key = (existing.get("created_at", ""), existing.get("id", ""))
        if current_key > existing_key:
            latest_by_sentence[sentence_id] = attempt

    return sorted(
        latest_by_sentence.values(),
        key=lambda item: (item.get("created_at", ""), item.get("id", "")),
        reverse=True,
    )


def get_next_practice(user_id, sentences, attempts, *, limit=10, level=None, pattern=None):
    response = _build_base_response(user_id, limit, level, pattern)
    sentence_index = _build_sentence_index(sentences, level=level, pattern=pattern)
    if not sentence_index:
        return response

    valid_sentence_ids = set(sentence_index.keys())
    user_attempts = _get_user_attempts(user_id, attempts, valid_sentence_ids)
    attempted_ids = {attempt.get("sentence_id") for attempt in user_attempts}

    weak_pattern_recommendations = []
    for weak_pattern in _get_weak_patterns(user_attempts):
        weak_pattern_recommendations.extend(
            _get_not_attempted_sentence_metas(
                sentence_index,
                attempted_ids,
                pattern=weak_pattern["pattern"],
            )
        )
        if len(weak_pattern_recommendations) >= limit:
            break

    if weak_pattern_recommendations:
        response["strategy"] = "weak_pattern_not_attempted"
        response["is_exhausted"] = False
        response["recommendations"] = _serialize_recommendations(
            weak_pattern_recommendations[:limit],
            "weak_pattern_not_attempted",
        )
        return response

    not_attempted_recommendations = _get_not_attempted_sentence_metas(sentence_index, attempted_ids)
    if not_attempted_recommendations:
        response["strategy"] = "not_attempted"
        response["is_exhausted"] = False
        response["recommendations"] = _serialize_recommendations(
            not_attempted_recommendations[:limit],
            "not_attempted",
        )
        return response

    latest_wrong_attempts = _get_latest_wrong_attempts(user_attempts)
    if latest_wrong_attempts:
        response["strategy"] = "recent_wrong_attempt"
        response["is_exhausted"] = False
        response["recommendations"] = _serialize_recommendations(
            [
                sentence_index[attempt["sentence_id"]]
                for attempt in latest_wrong_attempts[:limit]
                if attempt.get("sentence_id") in sentence_index
            ],
            "recent_wrong_attempt",
        )
        return response

    return response


class RecommendationStore:
    def __init__(self, sentences, attempts_store):
        self.sentences = list(sentences)
        self.attempts_store = attempts_store

    def get_next_practice(self, user_id, *, limit=10, level=None, pattern=None):
        return get_next_practice(
            user_id,
            self.sentences,
            self.attempts_store.get_all_attempts(),
            limit=limit,
            level=level,
            pattern=pattern,
        )

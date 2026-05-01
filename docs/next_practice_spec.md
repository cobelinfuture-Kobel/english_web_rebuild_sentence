# Next Practice Recommendation Spec

## Status

Planned.

This document defines the first rule-based recommendation API for the English sentence practice system.

The API is not implemented yet.

## Goal

Add a backend API that can answer:

```text
What should this user practice next?
Why are these sentences recommended?
```

The first version should be rule-based only.

Do not implement:

* AI recommendation
* forgetting curve
* mastery score
* adaptive difficulty
* frontend UI
* wrong-answer retry mode
* manifest generation
* database migration

## API

```http
GET /api/users/<id>/next-practice
```

Optional query string:

```text
limit=10
level=A1
pattern=SHOP_PAY
```

## Query Rules

### limit

* Default: `10`
* Use only when it is a valid positive integer.
* If invalid, fall back to `10`.

### level

* If provided, recommend only sentences from that level.
* If omitted, do not restrict by level.

### pattern

* If provided, recommend only sentences from that pattern.
* If omitted, do not restrict by pattern.

### Filter Priority

`level` and `pattern` filters take priority over recommendation logic.

Example:

```text
Request: level=A2
A2 has no available recommendation.
A1 has recent wrong answers.
```

Expected result:

```json
{
  "strategy": "none",
  "is_exhausted": true,
  "recommendations": []
}
```

The API must not ignore the filter and recommend A1 sentences.

## Response Format

### With Recommendations

```json
{
  "user_id": "user_001",
  "strategy": "weak_pattern_not_attempted",
  "is_exhausted": false,
  "limit": 10,
  "filters": {
    "level": "A1",
    "pattern": null
  },
  "recommendations": [
    {
      "sentence_id": "SHOP_TOO_A1_002",
      "level": "A1",
      "pattern": "SHOP_TOO",
      "reason": "weak_pattern_not_attempted"
    }
  ]
}
```

### Without Recommendations

```json
{
  "user_id": "user_001",
  "strategy": "none",
  "is_exhausted": true,
  "limit": 10,
  "filters": {
    "level": null,
    "pattern": null
  },
  "recommendations": []
}
```

## Recommendation Priority

### Priority 1: Unattempted Sentences in Weak Patterns

A pattern is weak when:

```text
total_attempts >= 5
accuracy < 0.7
```

If weak patterns exist and there are unattempted sentences in those patterns, recommend those sentences first.

Strategy:

```text
weak_pattern_not_attempted
```

Reason:

```text
weak_pattern_not_attempted
```

### Multiple Weak Patterns

If multiple weak patterns qualify, sort weak patterns by:

```text
accuracy ASC
wrong_attempts DESC
pattern ASC
```

Then collect recommendations in that order.

Example:

```text
SHOP_TOO accuracy = 0.4, has 3 unattempted sentences
SHOP_PAY accuracy = 0.6, has 10 unattempted sentences
limit = 10
```

Expected behavior:

```text
Take 3 from SHOP_TOO.
Then take 7 from SHOP_PAY.
```

This is weakest-first allocation, not fair distribution.

### Priority 2: General Unattempted Sentences

If Priority 1 has no available recommendation, recommend general unattempted sentences.

Strategy:

```text
not_attempted
```

Reason:

```text
not_attempted
```

### Priority 3: Recent Wrong Attempts

If there are no available unattempted sentences, recommend recent wrong attempts.

Strategy:

```text
recent_wrong_attempt
```

Reason:

```text
recent_wrong_attempt
```

### Priority 4: No Recommendation

If no recommendation is available:

```text
strategy = none
is_exhausted = true
recommendations = []
```

## Limit Semantics

Version 1 uses single-strategy responses.

Do not mix different strategies in one response.

Example:

```text
strategy = weak_pattern_not_attempted
limit = 10
Only 3 weak-pattern unattempted sentences are available.
```

Expected behavior:

```text
Return only 3 recommendations.
Do not fill the remaining 7 with general unattempted sentences.
```

Exception:

Multiple weak patterns still belong to the same strategy, so they may fill the same response up to the limit.

## Sorting Rules

### General Unattempted Sentences

Sort by:

```text
level ASC
pattern ASC
sentence_id ASC
```

### Weak Patterns

Sort by:

```text
accuracy ASC
wrong_attempts DESC
pattern ASC
```

### Sentences Inside a Weak Pattern

Sort by:

```text
level ASC
pattern ASC
sentence_id ASC
```

### Recent Wrong Attempts

Sort by:

```text
created_at DESC
id DESC
```

If the same `sentence_id` has multiple wrong attempts, return only the latest one.

## Metadata Source

The response fields below must come from the sentence bank:

```text
sentence_id
level
pattern
```

Do not use attempt metadata as the primary source.

Reason:

```text
attempts may contain old metadata
sentence bank is the current valid universe
```

## Store Design

Recommended new module:

```text
stores/recommendation_store.py
```

Recommended core function:

```python
def get_next_practice(
    user_id: str,
    sentences: list[dict],
    attempts: list[dict],
    *,
    limit: int = 10,
    level: str | None = None,
    pattern: str | None = None,
) -> dict:
    ...
```

This function should be pure logic:

* no file reads
* no file writes
* no Flask dependency
* no direct sentence_engine dependency
* no JSON path dependency

`app.py` should load the sentence bank and attempts, then pass them into the recommendation function.

## API Error Rules

If user does not exist:

```http
404
```

Response:

```json
{
  "error": "User not found"
}
```

## Test Plan

When implementing this API later, add tests for:

1. User does not exist -> 404.
2. No sentence bank -> `strategy = none`, `is_exhausted = true`.
3. No attempts -> `strategy = not_attempted`.
4. Weak pattern exists and has unattempted sentences -> `strategy = weak_pattern_not_attempted`.
5. Multiple weak patterns are sorted by `accuracy ASC`, `wrong_attempts DESC`, `pattern ASC`.
6. Weak-pattern recommendations fewer than `limit` do not get filled by general unattempted sentences.
7. Weak pattern sentences all attempted -> fallback to general unattempted sentences.
8. All sentences attempted and wrong attempts exist -> fallback to recent wrong attempts.
9. All sentences attempted and no wrong attempts -> `strategy = none`, `is_exhausted = true`.
10. Valid `limit` restricts total recommendations.
11. Invalid `limit` falls back to `10`.
12. `level` filter works.
13. `pattern` filter works.
14. `level + pattern` filters work together.
15. Filters take priority over recommendation logic.
16. Other users' attempts do not affect the result.
17. Multiple attempts for the same `sentence_id` count as attempted only once.
18. Multiple wrong attempts for the same `sentence_id` return only the latest one.
19. Recommendation metadata uses the sentence bank, not attempt metadata.
20. Recommendation sorting is deterministic.

## Suggested Implementation Commit

When this spec is implemented later, use:

```text
feat: add next practice API
```

For this documentation-only change, use:

```text
docs: add next practice recommendation spec
```

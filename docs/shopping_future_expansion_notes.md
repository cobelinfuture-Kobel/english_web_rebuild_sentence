# Shopping Future Expansion Notes

## Status

Shopping v1 is complete and reviewed for:

- A1
- A1+
- A2
- A2+
- B1

## Stable Rules from Shopping v1

The following rules are considered stable and should be preserved unless there is a strong semantic reason to redesign them:

- `SHOP_TOO` uses paired semantic slots.
- `SHOP_PAY` uses `pay with`, not `pay by`.
- Payment locations are restricted.
- `for school` uses `school_items_single`.
- A2+ reason clauses use positive reason pairs.
- B1 damage and material patterns use paired slots.
- American English is the default.

## Deferred Phase 2 Ideas

The following ideas are intentionally deferred to Shopping Phase 2:

- plural reason clauses with `they are`
- B1 color exchange
- found-damage pattern
- material search pattern
- conditional exchange
- equal comparison
- `faded`
- `silk`
- `one size fits all`

These ideas may be useful later, but they are not required for Shopping v1.

## Deferral Rule

Do not implement these Phase 2 ideas until another scenario needs the same abstraction or Shopping v2 begins.

# Global Grammar Expansion Plan: Pronouns, Possessives, Number, and Agreement

## Status

Planned.

This document defines a global grammar expansion plan for the sentence-bank and FSI drill system.

It applies across:

- Shopping
- Food & Drink
- Daily Routine

The current project is strongly scenario-based and learner-centered.

Most generated sentences currently focus on:

```text
I
my
you-questions
Can I ...
present simple
fixed polite chunks
scenario-specific vocabulary
```

This keeps early sentence generation semantically safe, but it also omits major grammar dimensions that learners eventually need.

This document defines how to add those grammar dimensions by level without breaking semantic safety or FSI quality.

This is a planning document only.

It does not change slot banks, pattern banks, generated sentence data, generator code, application code, or tests.

## Core Purpose

The goal is not to add random grammar.

The goal is to define a Cambridge / CEFR-aligned grammar scope for A1 through B1 and then apply it through grammar-safe FSI substitution.

The plan must support:

```text
level-appropriate grammar
scenario-appropriate language
FSI-style repetition
chunk substitution
grammar substitution
semantic compatibility
```

The central principle is:

```text
Cambridge / CEFR controls level appropriateness.
FSI controls repetition and substitution density.
Semantic rules control naturalness.
Grammar-safe pairing controls agreement.
```

## Why This Plan Is Needed

The current scenario banks under-cover several grammar dimensions:

```text
singular / plural
I / you / he / she / it / we / they
my / your / his / her / its / our / their
be agreement: I am / you are / he is / they are
have agreement: I have / he has / they have
present simple agreement: I clean / he cleans
articles: a / an / the
this / that / these / those
countable / uncountable nouns
some / any / much / many
basic connectors
comparatives and superlatives
basic tense roadmap
```

These are necessary for a full English sentence-rebuild and FSI drill system.

However, they cannot be added as free substitution lists.

Bad design:

```json
{
  "subject": ["I", "you", "he", "she", "we", "they"],
  "verb": ["clean", "cleans"],
  "possessive": ["my", "your", "his", "her", "our", "their"]
}
```

This would generate errors such as:

```text
He clean my room.
They cleans their room.
We has our books.
She brush your teeth.
```

Correct design requires paired grammar slots.

Example:

```json
[
  {
    "subject": "I",
    "verb": "clean",
    "possessive": "my",
    "object": "room"
  },
  {
    "subject": "you",
    "verb": "clean",
    "possessive": "your",
    "object": "room"
  },
  {
    "subject": "he",
    "verb": "cleans",
    "possessive": "his",
    "object": "room"
  },
  {
    "subject": "she",
    "verb": "cleans",
    "possessive": "her",
    "object": "room"
  },
  {
    "subject": "we",
    "verb": "clean",
    "possessive": "our",
    "object": "rooms"
  },
  {
    "subject": "they",
    "verb": "clean",
    "possessive": "their",
    "object": "rooms"
  }
]
```

Frame:

```text
{subject} {verb} {possessive} {object}.
```

Outputs:

```text
I clean my room.
You clean your room.
He cleans his room.
She cleans her room.
We clean our rooms.
They clean their rooms.
```

This is the required model for grammar-safe FSI.

## Global Level Grammar Scope

This section defines the broad grammar scope for A1 through B1.

It is not a strict textbook sequence.

It is a project-level implementation scope for controlled sentence generation.

## A1 Grammar Scope

A1 should focus on concrete, high-frequency, low-risk grammar.

Recommended A1 grammar dimensions:

```text
I / you
my / your
this / that
singular concrete nouns
basic plural nouns only in fixed chunks
be: I am / you are / it is
have: I have / you have
present simple first-person
simple imperatives
simple yes/no chunks
basic prepositions of place: in / on / at
basic question words: what / where / who
basic articles: a / an / the
```

A1 examples:

```text
I have my book.
You have your bag.
I am ready.
You are ready.
It is morning.
This is my bag.
That is my book.
I am at school.
The book is on the table.
What is this?
Where is my bag?
Who is he?
I want a book.
I have an apple.
```

A1 should avoid:

```text
broad he/she verb-s generation
broad we/they plural agreement
because clauses
general past tense
complex time clauses
comparatives
superlatives
open-ended paragraph output
```

### A1 Scenario Notes

Shopping:

```text
This is a shirt.
That is a bag.
I want a book.
Where is the shop?
```

Food & Drink:

```text
I want an apple.
I have a banana.
This is water.
Where is my lunch?
```

Daily Routine:

```text
I have my book.
I am at school.
The book is on the table.
I brush my teeth.
```

## A1+ Grammar Scope

A1+ may introduce slightly expanded interaction and high-frequency chunks.

Recommended A1+ grammar dimensions:

```text
he / she / it in controlled be frames
his / her in controlled item frames
simple time phrases
like to / want to + base verb
basic frequency adverbs: always / never
basic can requests
simple plural nouns in fixed chunks
```

A1+ examples:

```text
He is ready.
She is busy.
He has his bag.
She has her book.
I like to listen to music.
I want to read a book today.
I always wash my face.
I never go to bed late.
Can I have a coffee, please?
Can I have this bag?
```

A1+ should still avoid broad free subject replacement.

For example, do not freely generate:

```text
He clean his room.
She brush her teeth.
```

If he/she present simple is used, it must be paired:

```text
He cleans his room.
She brushes her teeth.
```

### A1+ Scenario Notes

Shopping:

```text
Can I have this bag?
Can I have a receipt?
I want this shirt.
```

Food & Drink:

```text
Can I have a coffee, please?
I want some water.
I like to drink milk.
```

Daily Routine:

```text
I always wash my face.
I never go to bed late.
He has his bag.
She has her book.
```

## A2 Grammar Scope

A2 can introduce broader subject variation and core grammar control.

Recommended A2 grammar dimensions:

```text
he / she / we / they
his / her / our / their
present simple agreement
do / does questions
can requests
need to / have to / would like to
plural nouns
countable / uncountable nouns
some / any / much / many
simple connectors: and / but / or
fixed past expression: I forgot ...
```

A2 examples:

```text
He cleans his room.
She brushes her teeth.
We pack our bags.
They have their books.
Does he have his book?
Do they have their lunch?
Can I use your pencil?
I need to pack my bag.
I would like some water.
Do you have any milk?
There isn't much water.
I want an apple and some milk.
I can eat here, but I cannot play here.
I forgot my homework.
```

A2 should treat `forgot` as a fixed high-frequency classroom or daily-life expression.

Allowed:

```text
I forgot my homework.
I forgot my book.
```

Not allowed as general expansion:

```text
Yesterday, I forgot my homework.
I went to school.
I bought a shirt.
I cleaned my room.
```

### A2 Scenario Notes

Shopping:

```text
Does he want this shirt?
Do they have these shoes?
Can I use your card?
This shirt is small, but it is cheap.
```

Food & Drink:

```text
Do you have any milk?
I would like some water.
There isn't much rice.
How many apples do you have?
```

Daily Routine:

```text
He cleans his room.
She brushes her teeth.
We pack our bags.
They have their books.
I forgot my homework.
```

## A2+ Grammar Scope

A2+ can combine controlled grammar with simple reasons, sequence, and manner.

Recommended A2+ grammar dimensions:

```text
because clauses
before / after sequence
cannot because
remind me to
permission with condition
controlled subject variation
adverbs of manner: slowly / carefully / well
comparatives in controlled frames
```

A2+ examples:

```text
He cleans his room because it is messy.
She packs her bag before school.
They cannot play because they have homework.
Please remind me to bring my book.
Can I watch TV after I finish my homework?
He brushes his teeth carefully.
She reads well.
This shirt is cheaper than that one.
This bag is bigger than that one.
```

A2+ grammar must use paired slots when necessary.

Bad:

```text
I drink water because I am sleepy.
I brush my teeth because I am hungry.
```

Good:

```json
{"action": "drink water", "reason": "I am thirsty"}
{"action": "brush my teeth", "reason": "I want clean teeth"}
{"action": "clean my room", "reason": "it is messy"}
```

### A2+ Scenario Notes

Shopping:

```text
This shirt is cheaper than that one.
This bag is bigger than that one.
I like this one because it is cheaper.
```

Food & Drink:

```text
This apple is sweeter than that one.
He eats slowly.
She cooks well.
I want some water because I am thirsty.
```

Daily Routine:

```text
He brushes his teeth carefully.
She packs her bag before school.
They cannot play because they have homework.
```

## B1 Grammar Scope

B1 can include controlled routine-management, decision-making, and more complex connected grammar.

Recommended B1 grammar dimensions:

```text
frequency adverbs
clock time
before / after subordinate clauses
It takes ... to ...
should
must
have to
reported rule: My parents say I have to ...
controlled comparison
superlatives
more complex prepositions of time: during / until / since
controlled multi-slot chunk substitution
```

B1 examples:

```text
He usually gets up at seven.
They usually clean their rooms on weekends.
It takes ten minutes to pack my bag.
Before I leave home, I check my bag.
After I finish my homework, I watch TV.
My parents say we have to finish our homework.
I should go to bed earlier.
You must wash your hands before dinner.
This is the best coffee here.
This is the cheapest shirt in the store.
I study during lunch.
I wait until six.
I have studied English since last year.
```

Important note:

`since` often implies perfect tense in natural English.

For B1 sentence generation, `since` should be deferred unless the project intentionally supports present perfect.

Safer B1 time prepositions:

```text
during
until
before
after
from ... to ...
```

B1 should still avoid uncontrolled:

```text
general past tense expansion
present perfect expansion
free relative clauses
paragraph generation
multi-turn dialogue
open-ended weekly calendar planning
```

### B1 Scenario Notes

Shopping:

```text
This is the cheapest shirt in the store.
This bag is better than that one.
You should keep the receipt.
You must show your card.
```

Food & Drink:

```text
This is the best coffee here.
You should drink more water.
We have to wait until six.
This meal is better than that one.
```

Daily Routine:

```text
Before I leave home, I check my bag.
After I finish my homework, I watch TV.
My parents say we have to finish our homework.
It takes ten minutes to pack my bag.
```

## Tense Roadmap

Tense must be handled separately from ordinary chunk substitution.

Current project state:

```text
Present simple is the main tense for A1-B1 scenario banks.
Some modal forms are used: can, need to, have to, would like to, should.
A2 may include fixed past chunks such as I forgot ...
General past tense is deferred.
Future forms are deferred or tightly controlled.
Present continuous is only allowed in fixed situational chunks.
```

## Present Simple

Primary tense for:

```text
Shopping
Food & Drink
Daily Routine
```

Examples:

```text
I want this shirt.
I drink water.
I clean my room.
He cleans his room.
They have their books.
```

Present simple expansion requires subject-verb agreement.

## Present Continuous

May be introduced as fixed or controlled chunks at A1+ / A2.

Recommended fixed patterns:

```text
I am looking for {item}.
I am eating {food}.
I am drinking {drink}.
```

Shopping example:

```text
I am looking for a gift.
```

Food example:

```text
I am eating an apple.
```

Daily Routine example:

```text
I am doing my homework.
```

Do not open full present continuous generation until the generator can safely control:

```text
be agreement
verb-ing forms
semantic compatibility
```

## Future Forms

Future should be deferred or controlled.

Possible later A2+ / B1 fixed patterns:

```text
I will take the steak.
I am going to clean my room.
We are going to eat dinner.
```

Risk:

```text
will + base verb
be going to + base verb
be agreement
```

Recommendation:

Keep future forms out of the current Phase 4C.

## Past Simple

Past simple should not be broadly enabled in the current A1-B1 scenario banks.

Allowed fixed expression:

```text
I forgot my homework.
I forgot my book.
```

Deferred general past examples:

```text
I went to school yesterday.
I bought a shirt.
I cleaned my room.
I ate breakfast.
```

Reason:

Past tense requires:

```text
regular verbs
irregular verbs
negative forms
questions
time markers
verb form control
```

This should be a dedicated later expansion.

## Present Perfect

Defer.

Do not use `since` freely unless present perfect is supported.

Risky:

```text
I study English since last year.
```

Natural:

```text
I have studied English since last year.
```

Because present perfect is not currently in scope, avoid `since` in generated B1 data unless explicitly implementing present perfect.

## FSI Grammar Substitution Model

The project should support two FSI dimensions.

## 1. Chunk Substitution

Example:

```text
I have {item}.
```

Outputs:

```text
I have my book.
I have my bag.
I have my lunch.
I have my homework.
```

This is lexical or chunk substitution.

## 2. Grammar Substitution

Example:

```text
{subject} {verb} {possessive} {object}.
```

Outputs:

```text
I clean my room.
You clean your room.
He cleans his room.
She cleans her room.
We clean our rooms.
They clean their rooms.
```

This requires paired grammar slots.

## Safe Grammar Pair Categories

Future slot banks may define categories such as:

```text
subject_be_pairs
subject_have_pairs
subject_present_simple_pairs
subject_possessive_object_pairs
subject_possessive_plural_pairs
this_that_these_those_item_pairs
countable_food_pairs
uncountable_food_pairs
shopping_demonstrative_item_pairs
routine_subject_action_pairs
```

## Scenario-Specific Grammar Expansion

## Shopping

Important grammar dimensions:

```text
this / that / these / those
it is / they are
a / an / the
singular / plural items
wants / want
cheaper / more expensive
best / cheapest
can requests
should / must
```

Examples:

```text
This shirt is cheap.
These shoes are expensive.
She wants this shirt.
They want these shoes.
Do you have this in blue?
Do you have these in blue?
This is the cheapest shirt in the store.
You should keep the receipt.
```

## Food & Drink

Important grammar dimensions:

```text
countable / uncountable nouns
a / an / some
any / much / many
it is / they are
wants / want
comparatives
superlatives
can requests
would like
```

Examples:

```text
I want an apple.
I want some water.
Do you have any milk?
There isn't much rice.
How many apples do you have?
This apple is sweeter than that one.
This is the best coffee here.
She wants a sandwich.
They want sandwiches.
```

## Daily Routine

Important grammar dimensions:

```text
subject pronouns
possessive determiners
present simple agreement
be agreement
have / has
do / does questions
singular / plural routine objects
before / after sequence
because clauses
should / have to / must
```

Examples:

```text
I clean my room.
You clean your room.
He cleans his room.
She brushes her teeth.
We pack our bags.
They do their homework.
Does he have his book?
Before I leave home, I check my bag.
After I finish my homework, I watch TV.
```

## Implementation Strategy

Do not implement this global grammar expansion in one step.

Recommended phases:

## Phase 5A: Documentation and Grammar Inventory

Add this document.

Then inspect existing pattern banks and slot banks for:

```text
where first-person-only assumptions exist
where my/your assumptions exist
where singular-only assumptions exist
where demonstrative forms already exist
where countable/uncountable handling already exists
where agreement risks exist
```

## Phase 5B: Daily Routine Pilot

Daily Routine is the safest pilot for grammar-aware FSI because its action frames are simple.

Pilot patterns:

```text
ROUTINE_SUBJECT_CLEAN_OBJECT
ROUTINE_SUBJECT_BRUSH_OBJECT
ROUTINE_SUBJECT_HAVE_ITEM
ROUTINE_SUBJECT_PACK_ITEM
ROUTINE_SUBJECT_BE_STATE
```

Use paired grammar slots.

Do not start with Shopping or Food & Drink because countability and demonstratives make them more complex.

## Phase 5C: Food & Drink Countability Expansion

Add grammar-safe countable / uncountable handling.

Pilot patterns:

```text
FOOD_WANT_COUNTABLE_SUBJECT
FOOD_WANT_UNCOUNTABLE_SUBJECT
FOOD_HAVE_ANY
FOOD_MUCH_MANY
FOOD_THIS_THAT_THESE_THOSE
```

## Phase 5D: Shopping Demonstrative and Number Expansion

Add this / that / these / those, singular/plural items, and it/they agreement.

Pilot patterns:

```text
SHOP_THIS_THAT_ITEM
SHOP_THESE_THOSE_ITEMS
SHOP_IT_IS_ADJ
SHOP_THEY_ARE_ADJ
SHOP_SUBJECT_WANT_ITEM
```

## Phase 5E: Tense Expansion

Only after agreement, number, and countability are stable.

Possible future docs:

```text
docs/grammar_expansion_tense_plan.md
docs/daily_routine_past_tense_extension_plan.md
docs/shopping_past_purchase_extension_plan.md
docs/food_drink_past_order_extension_plan.md
```

## Risk Controls

## 1. No free pronoun replacement

Bad:

```text
I clean my room.
He clean my room.
They clean my room.
```

Good:

```text
I clean my room.
He cleans his room.
They clean their rooms.
```

## 2. No free possessive replacement

Bad:

```text
She brushes my teeth.
They pack his bags.
```

Good:

```text
She brushes her teeth.
They pack their bags.
```

## 3. No free singular/plural replacement

Bad:

```text
These shirt is cheap.
This shoes are expensive.
```

Good:

```text
This shirt is cheap.
These shoes are expensive.
```

## 4. No free countable/uncountable replacement

Bad:

```text
I want a water.
I want many milk.
```

Good:

```text
I want some water.
I want much milk.
I want an apple.
I want many apples.
```

## 5. No broad tense mixing

Bad:

```text
I went to school every day.
He clean his room yesterday.
I have studied English since last year.
```

unless the required tense system is explicitly implemented.

## Tests Needed Later

Future tests should verify:

```text
subject-verb agreement
be agreement
have/has agreement
possessive agreement
this/that/these/those agreement
singular/plural noun agreement
countable/uncountable determiner agreement
some/any/much/many usage
no uncontrolled past tense
no uncontrolled present perfect
no free pronoun replacement
scenario-specific semantic compatibility
```

Example tests:

```python
def test_no_bad_subject_verb_agreement(sentences):
    bad_phrases = [
        "He clean ",
        "She clean ",
        "He brush ",
        "She brush ",
        "They cleans ",
        "We has ",
    ]
    for s in sentences:
        assert not any(x in s["target_sentence"] for x in bad_phrases)


def test_no_bad_possessive_agreement(sentences):
    bad_phrases = [
        "She brushes my teeth",
        "He packs her bag",
        "They pack his bag",
    ]
    for s in sentences:
        assert not any(x in s["target_sentence"] for x in bad_phrases)


def test_no_bad_countability(sentences):
    bad_phrases = [
        "a water",
        "an water",
        "many milk",
        "much apples",
    ]
    for s in sentences:
        assert not any(x in s["target_sentence"] for x in bad_phrases)
```

## Completion Criteria

This global grammar expansion plan is accepted when:

```text
1. A1 through B1 grammar scope is documented.
2. Pronoun / possessive / number / agreement risks are documented.
3. Articles, prepositions, question words, countability, quantifiers, connectors, comparatives, superlatives, and modals are documented by level.
4. Tense roadmap is documented.
5. Shopping, Food & Drink, and Daily Routine scenario implications are documented.
6. Safe paired-slot implementation strategy is documented.
7. Deferred grammar areas are clearly separated.
```

## Status

Planned.

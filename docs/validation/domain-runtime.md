# Domain Runtime Validation

Runtime domain validation provides **best-effort semantic checks**
on OMOP objects during interactive or analytical use.

These checks answer a simple but critical question:

> “Does this object reference concepts from the domains it claims to?”

---

## Domain validation is advisory

Runtime validation in OMOP Alchemy is:

- non-blocking
- non-mutating
- safe to run interactively
- safe to skip entirely

It is designed to *surface issues*, not enforce policy.

This makes it suitable for:

- notebooks
- exploratory analysis
- cohort debugging
- governance and QA workflows

---

## `DomainValidationMixin`

Domain runtime validation is provided via `DomainValidationMixin`,
which is intended for **View classes only**.

::: omop_alchemy.cdm.base.domain_validation.DomainValidationMixin
    options:
      heading_level: 3

The mixin relies on:

- declared expectations
- an active SQLAlchemy session (if available)
- the OMOP `Concept` table

---

## Runtime checking behavior

At runtime, domain validation:

- resolves referenced concept IDs
- checks their `domain_id`
- compares against expected domains
- reports violations as human-readable messages

OMOP conventions are respected:

- `concept_id = 0` is always treated as valid
- detached objects are handled safely

---

## Example usage

```python
p = session.get(PersonView, 123)

p.is_domain_valid
```

Returns `True` or `False`.

To inspect violations directly:

```python
p.domain_violations
```

Example output:

```
[
  "gender_concept_id not in domain(s): ['Gender']"
]
```

---

## What happens under the hood

For each declared field:

1. The referenced `concept_id` is retrieved
2. The corresponding Concept row is resolved
3. The concept’s `domain_id` is compared
4. Violations are accumulated, not raised

---

## When *not* to use runtime validation

Runtime validation is not a substitute for:

- ETL quality checks
- database constraints
- DataQualityDashboard or similar systematic QA tooling

Those tools operate at a different layer, with different goals. It complements those tools by operating at the **model and object layer**.

> “Does this object, *in this analytical context*, behave the way I think it does?”

That’s a much more local question, and one that usually arises:

* during exploration
* while building derived views
* or when debugging unexpected analytical results

i.e. not asking whether the database as a whole is valid but trying to understand whether the meaning of what you’re looking at holds.

### Why an object-level approach helps

Many semantic problems don’t show up cleanly in ETL or database checks:

* a view joins concept IDs that are technically valid but conceptually incompatible
* a derived cohort quietly mixes domains in a way that undermines interpretation
* a field is populated, but with concepts that don’t make sense for this specific use

Custom DQD checks expressed in SQL can handle these local constraints requiring additional context, however these issues are often easiest to spot when you’re already holding the data in your hands. Runtime validation takes advantage of object mappings to support that task by making expectations explicit and inspectable.

* DQD establishes baseline trust in the dataset
* OMOP Alchemy helps maintain semantic clarity during analytical work

### Next steps

...come back soon for LinkML support
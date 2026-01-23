# Domain Rules

Domain rules describe **expected OMOP concept domains**
for specific fields on OMOP tables or views.

They are represented explicitly using the `DomainRule` model.


These expectations are **not enforced by the database** and are often
*not enforced by ETL pipelines* — which is precisely why they need to be
documented and validated explicitly.

---

## Declaring expected domains

::: omop_alchemy.cdm.base.domain_validation.DomainRule
    options:
      heading_level: 3

### Why rules are generated, not authored

OMOP Alchemy does **not** encourage manually writing domain rules.

Instead, rules are **derived from model declarations** to ensure:

- rules stay co-located with semantic intent
- documentation cannot drift from code
- tooling can introspect expectations automatically

Domain rules are collected from *View classes* that declare
their expectations explicitly.

## The ExpectedDomain Model

::: omop_alchemy.cdm.base.domain_validation.ExpectedDomain
    options:
      heading_level: 3

## Use on View Classes

Expected domains are declared on View classes using
`__expected_domains__`.

::: omop_alchemy.cdm.base.domain_validation.DomainValidationMixin
    options:
      heading_level: 3

---

## Collecting rules programmatically

Declared rules can be collected into canonical `DomainRule` objects:

```python
PersonView.collect_domain_rules()
```

Which yields:

```python
[
    DomainRule(
        table="person",
        field="gender_concept_id",
        allowed_domains={"Gender"},
    ),
    DomainRule(
        table="person",
        field="race_concept_id",
        allowed_domains={"Race"},
    ),
]
```

This allows domain rules to be:

- documented
- audited
- exported
- validated across the model layer

---

## What domain rules are *not*

Domain rules intentionally do **not**:

- enforce ETL behavior
- mutate data
- raise hard exceptions
- assume any execution environment

They exist to make *semantic expectations visible and checkable* —
not to constrain ingestion workflows.
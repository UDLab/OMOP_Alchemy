# Validation

OMOP Alchemy provides **semantic validation utilities** for working with
OMOP CDM data safely and intentionally.

Validation in this context focuses on:

- whether OMOP conventions are respected in practice
- whether analytical views are logically coherent

---

## What lives here

The validation layer covers:

- OMOP **domain constraints** (e.g. gender concepts must be from the Gender domain)
- Concept-level semantic checks
- View-scoped expectations
- Lightweight runtime diagnostics



It distinguishes between **structural correctness** and
**semantic correctness**.

Structural validation (tables, columns, keys, loadability) is handled by
lower-level infrastructure in `orm-loader`.



---

## Structural vs semantic validation

| Layer | Responsibility |
|------|---------------|
| Database | Physical constraints, indexes |
| orm-loader | Table structure, keys, loadability, handle dirty and untrusted data sources |
| OMOP Alchemy | Meaning, domains, concept semantics |

This separation ensures:

- reusable infrastructure
- OMOP-specific logic stays OMOP-specific
- validation can evolve independently of ingestion


---

## Validation scope

Currently supported validation includes:

- domain conformity checks
- concept-level sanity checks
- view-level semantic expectations

Future extensions may include:

- value set adherence
- temporal logic checks
- cross-table semantic consistency


---

## Rule specification and documentation

Domain rules are generated from View classes via collect_domain_rules() rather than being authored manually.

- [Domain Rules](domain-rules.md)

## Runtime usage

Interactive checking of object conformance

- [Domain Runtime](domain-runtime.md)
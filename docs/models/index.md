# OMOP Models

OMOP Alchemy defines ORM models corresponding to the official OMOP CDM tables,
organised by clinical and operational domain.

Models are fully typed, relationship-aware, and designed for safe querying,
validation, and reuse.

---

## Clinical Data

- [Person](clinical/person.md)
- [Condition Occurrence](clinical/condition_occurrence.md)
- [Drug Exposure](clinical/drug_exposure.md)
- [Measurement](clinical/measurement.md)
- [Observation](clinical/observation.md)

---

## Health System Structure

- [Visit Occurrence](health_system/visit_occurrence.md)
- [Visit Detail](health_system/visit_detail.md)
- [Care Site](health_system/care_site.md)
- [Provider](health_system/provider.md)
- [Location](health_system/location.md)

---

## Vocabulary & Concepts

- [Concept](vocabulary/concept.md)
- [Domain](vocabulary/domain.md)
- [Vocabulary](vocabulary/vocabulary.md)
- [Concept Relationships](vocabulary/concept_relationship.md)

---

## Derived & Extended Models

- [Condition Era](derived/condition_era.md)
- [Drug Era](derived/drug_era.md)
- [Dose Era](derived/dose_era.md)
- [Cohort & Cohort Definitions](derived/cohort.md)

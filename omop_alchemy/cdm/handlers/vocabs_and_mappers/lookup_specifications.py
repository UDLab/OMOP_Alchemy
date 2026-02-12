from .typing import LookupSpec
from .vocab_helpers import normalize_default, compose_normalizers, strip_uicc, site_to_NOS
from ...model.vocabulary import Concept

LOOKUP_SPECS = {
    "gender": LookupSpec(
        name="gender",
        domain_id="Gender",
        standard_only=True,
        unknown=0,
    ),
    "unit": LookupSpec(
        name="unit",
        domain_id="Unit",
        standard_only=True,
        unknown=0,
    ),
    "race": LookupSpec(
        name="race",
        domain_id="Race",
        standard_only=True,
        unknown=0,
    ),
    "ethnicity": LookupSpec(
        name="ethnicity",
        domain_id="Ethnicity",
        standard_only=True,
        unknown=0,
    ),
    "grading": LookupSpec(
        name="grading",
        domain_id="Measurement",
        concept_class_id=["Staging/Grading"],
        code_filter="grade",
        standard_only=True,
        unknown=0,
    ),
    # "mets": LookupSpec(
    #     name="mets",
    #     parents=[ConditionModifiers.mets.value],
    #     standard_only=True,
    #     unknown=0,
    # ),
    # "stage_edition": LookupSpec(
    #     name="stage_edition",
    #     parents=[ConditionModifiers.tnm.value],
    #     standard_only=True,
    #     unknown=0,
    #     normalizer=compose_normalizers(
    #         normalize_default,
    #         strip_uicc,
    #     ),
    # ),
    "icdo_condition": LookupSpec(
        name="icdo_condition",
        domain_id="Condition",
        concept_class_id=["ICDO Condition"],
        standard_only=False,
        unknown=0,
        normalizer=compose_normalizers(
            normalize_default,
            site_to_NOS,
        ),
    ),
    "icd10_condition": LookupSpec(
        name="icd10_condition",
        domain_id="Condition",
        concept_class_id=["ICD10 Hierarchy", "ICD10 code"],
        standard_only=False,
        unknown=0,
        normalizer=compose_normalizers(
            normalize_default,
            site_to_NOS,
        ),
    ),
    "relaxed_condition": LookupSpec(
        name="relaxed_condition",
        domain_id="Condition",
        vocabulary_id=["ICD10", "ICD10CM", "ICD9CM"],
        standard_only=False,
        unknown=0,
    ),
    # "radiotherapy_procedures": LookupSpec(
    #     name="radiotherapy_procedures",
    #     parents=[CancerProcedureTypes.rt_procedure.value],
    #     standard_only=True,
    #     unknown=0,
    # ),
}

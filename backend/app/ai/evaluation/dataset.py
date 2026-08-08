from dataclasses import dataclass
from typing import Literal


EvaluationCategory = Literal[
    "answerable",
    "synthesis",
    "unanswerable",
]


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_answer: str
    category: EvaluationCategory
    expected_source_contains: str | None = None


EVALUATION_CASES: list[EvaluationCase] = [
    # ---------------------------------------------------------
    # Answerable
    # ---------------------------------------------------------

    EvaluationCase(
        question="What is actual cash value?",
        expected_answer=(
            "Actual cash value is the value of property based on the "
            "current cost to replace it minus depreciation."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What does collision coverage pay for?",
        expected_answer=(
            "Collision coverage pays for damage to a car regardless "
            "of who caused the accident. The company pays for the "
            "repair or up to the actual cash value of the vehicle, "
            "minus the deductible."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What does comprehensive coverage protect against?",
        expected_answer=(
            "Comprehensive coverage pays for damage to or loss of an "
            "automobile from causes other than accidents, including "
            "hail, vandalism, flood, fire, and theft."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What is an insurance deductible?",
        expected_answer=(
            "A deductible is the amount the insured must pay in a "
            "loss before any payment is due from the insurance company."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What does gap insurance cover?",
        expected_answer=(
            "Gap insurance pays the difference between the actual cash "
            "value of a vehicle and the amount still owed on the loan. "
            "Some gap policies may also cover the deductible."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What is liability insurance?",
        expected_answer=(
            "Liability insurance is auto coverage that pays for "
            "injuries to another party and damage to another vehicle "
            "resulting from an accident caused by the policyholder or "
            "someone covered by the policy."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What does rental reimbursement coverage pay for?",
        expected_answer=(
            "Rental reimbursement coverage pays a set daily amount "
            "for a rental car while the policyholder's car is being "
            "repaired because of damage covered by the auto policy."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What is uninsured or underinsured motorist coverage?",
        expected_answer=(
            "Uninsured or underinsured motorist coverage is optional "
            "auto insurance that pays for the policyholder's bodily "
            "injuries when the other motorist has no liability "
            "insurance or insufficient coverage."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question="What is replacement cost coverage?",
        expected_answer=(
            "Replacement cost coverage pays the amount needed to "
            "replace a structure or damaged personal property without "
            "deducting for depreciation, subject to the policy's "
            "maximum dollar amount."
        ),
        category="answerable",
        expected_source_contains="CommonInsuranceTerms",
    ),

    # ---------------------------------------------------------
    # Ambiguous / synthesis
    # ---------------------------------------------------------

    EvaluationCase(
        question=(
            "What is the difference between actual cash value and "
            "replacement cost?"
        ),
        expected_answer=(
            "Actual cash value is based on the current replacement "
            "cost minus depreciation. Replacement cost coverage pays "
            "the amount needed to replace the property without "
            "deducting for depreciation, subject to the policy limit."
        ),
        category="synthesis",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question=(
            "What is the difference between collision coverage and "
            "comprehensive coverage?"
        ),
        expected_answer=(
            "Collision coverage pays for damage to a car resulting "
            "from an accident regardless of who caused it. "
            "Comprehensive coverage pays for automobile damage or "
            "loss from causes other than accidents, such as hail, "
            "vandalism, flood, fire, and theft."
        ),
        category="synthesis",
        expected_source_contains="CommonInsuranceTerms",
    ),

    EvaluationCase(
        question=(
            "What is the difference between a first-party claim and "
            "a third-party claim?"
        ),
        expected_answer=(
            "A first-party claim is filed by an insured against their "
            "own insurance policy. A third-party claim is filed "
            "against another person's insurance policy."
        ),
        category="synthesis",
        expected_source_contains="CommonInsuranceTerms",
    ),

    # ---------------------------------------------------------
    # Unanswerable / hallucination tests
    # ---------------------------------------------------------

    EvaluationCase(
        question="How much does car insurance cost per month?",
        expected_answer=(
            "The indexed document does not contain enough information "
            "to determine the monthly cost of car insurance."
        ),
        category="unanswerable",
        expected_source_contains=None,
    ),

    EvaluationCase(
        question="Which insurance company has the cheapest auto insurance?",
        expected_answer=(
            "The indexed document does not contain information about "
            "insurance company prices or which company is cheapest."
        ),
        category="unanswerable",
        expected_source_contains=None,
    ),

    EvaluationCase(
        question="What auto insurance coverage should I personally buy?",
        expected_answer=(
            "The indexed document does not provide enough information "
            "to recommend which auto insurance coverage a particular "
            "person should purchase."
        ),
        category="unanswerable",
        expected_source_contains=None,
    ),
]
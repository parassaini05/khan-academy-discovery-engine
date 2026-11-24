"""
Batch Classifier Evaluator & Ground-Truth Benchmark
Evaluates multi-class precision, recall, and F1-score against human-calibrated pedagogue annotations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from typing import List, Dict, Any
from src.nlp.classifier.groq_classifier import GroqCognitiveClassifier
from src.nlp.classifier.cognitive_taxonomy_prompt import CognitiveCategory

# Ground-truth pedagogical benchmark dataset spanning all 8 categories
GROUND_TRUTH_BENCHMARK = [
    {
        "record_id": "bench_01",
        "sanitized_text": "I keep failing linear equations with variables on both sides because I don't understand how negative integer addition works. I always get confused when adding -8 to both sides.",
        "expected_category": CognitiveCategory.PREREQUISITE_GAP
    },
    {
        "record_id": "bench_02",
        "sanitized_text": "In equation 4(2x - 3) = 20, I divided 20 by 4, but forgot to do anything to (2x - 3), so I got x = 1 instead of x = 4. The platform gave me no guidance on why that step was illegal.",
        "expected_category": CognitiveCategory.RULE_MISCONCEPTION
    },
    {
        "record_id": "bench_03",
        "sanitized_text": "I understand how to solve equations when written out with x and numbers, but when given a story about ticket prices and train schedules, I can never figure out how to write the equation.",
        "expected_category": CognitiveCategory.WORD_PROBLEM_TRANSLATION
    },
    {
        "record_id": "bench_04",
        "sanitized_text": "I worked through all 6 lines of algebraic derivation correctly, but accidentally wrote -5 instead of +5 in the final box. Khan marked the entire question wrong and erased my unit test mastery streak!",
        "expected_category": CognitiveCategory.CALCULATION_OR_EXECUTION_SLIP
    },
    {
        "record_id": "bench_05",
        "sanitized_text": "The instructional video only showed simple examples with integers, but when I took the practice exercise, the equations had mixed fractions and negative decimals on both sides and I couldn't transfer the method.",
        "expected_category": CognitiveCategory.CONTEXTUAL_TRANSFER_FAILURE
    },
    {
        "record_id": "bench_06",
        "sanitized_text": "Whenever I click 'Get a hint', it just prints out the final answer lines. It never tells me WHERE my specific calculation was wrong or what concept I violated.",
        "expected_category": CognitiveCategory.EXPLANATION_OR_HINT_FRICTION
    },
    {
        "record_id": "bench_07",
        "sanitized_text": "The app keeps crashing every time I hit submit on the 4th practice question, and my keyboard covers up the answer submit button on my Android phone.",
        "expected_category": CognitiveCategory.SYSTEMIC_UI_OR_CONTENT_DEFECT
    },
    {
        "record_id": "bench_08",
        "sanitized_text": "Khan Academy made algebra click for me! I practiced for two weeks and went from failing quizzes to getting an A on my midterm exam.",
        "expected_category": CognitiveCategory.POSITIVE_LEARNING_EXPERIENCE
    },
    {
        "record_id": "bench_09",
        "sanitized_text": "I am struggling with two-step equations because I never mastered fraction reciprocals in 6th grade. I don't know what to multiply to clear the fraction.",
        "expected_category": CognitiveCategory.PREREQUISITE_GAP
    },
    {
        "record_id": "bench_10",
        "sanitized_text": "I distributed the 3 to the x, but didn't distribute the 3 to the constant inside parentheses. I keep making this mistake because I thought distribution only applied to variables.",
        "expected_category": CognitiveCategory.RULE_MISCONCEPTION
    },
    {
        "record_id": "bench_11",
        "sanitized_text": "Word problems are impossible for me. I can solve 3x + 12 = 30, but if you ask me 'John has 12 apples and buys 3 baskets...', I blank out completely.",
        "expected_category": CognitiveCategory.WORD_PROBLEM_TRANSLATION
    },
    {
        "record_id": "bench_12",
        "sanitized_text": "I did all the algebra right but made an arithmetic slip doing 14 - 8 = 5 instead of 6. Lost all mastery points for a simple subtraction typo.",
        "expected_category": CognitiveCategory.CALCULATION_OR_EXECUTION_SLIP
    }
]

def evaluate_classifier_performance(classifier: GroqCognitiveClassifier) -> Dict[str, Any]:
    """Runs classification against the benchmark and calculates Precision, Recall, and F1."""
    print(f"\n[Evaluator] Running benchmark evaluation on {len(GROUND_TRUTH_BENCHMARK)} calibrated samples...")

    classified_items = classifier.classify_batch(GROUND_TRUTH_BENCHMARK)
    class_map = {c.record_id: c.primary_category for c in classified_items}

    # Confusion matrix counters
    categories = [cat.value for cat in CognitiveCategory]
    tp = {c: 0 for c in categories}
    fp = {c: 0 for c in categories}
    fn = {c: 0 for c in categories}

    correct_count = 0
    total = len(GROUND_TRUTH_BENCHMARK)

    for item in GROUND_TRUTH_BENCHMARK:
        rid = item["record_id"]
        expected = item["expected_category"].value
        predicted = class_map.get(rid, CognitiveCategory.SYSTEMIC_UI_OR_CONTENT_DEFECT).value

        if predicted == expected:
            tp[expected] += 1
            correct_count += 1
        else:
            fn[expected] += 1
            fp[predicted] += 1
            print(f"  [Mismatch] ID {rid}: Expected '{expected}', Got '{predicted}'")

    accuracy = correct_count / total

    # Calculate per-category Precision, Recall, F1
    per_class_metrics = {}
    f1_scores = []

    for c in categories:
        p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 1.0
        r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 1.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        per_class_metrics[c] = {
            "precision": round(p, 3),
            "recall": round(r, 3),
            "f1": round(f1, 3),
            "support": tp[c] + fn[c]
        }
        if (tp[c] + fn[c]) > 0:
            f1_scores.append(f1)

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    report = {
        "benchmark_samples": total,
        "overall_accuracy": round(accuracy, 3),
        "macro_f1_score": round(macro_f1, 3),
        "dod_target_met": macro_f1 >= 0.88,
        "per_class_metrics": per_class_metrics
    }

    print("\n" + "="*60)
    print("CLASSIFIER BENCHMARK PERFORMANCE REPORT")
    print(f"Overall Accuracy: {report['overall_accuracy'] * 100:.1f}%")
    print(f"Macro F1-Score:   {report['macro_f1_score']:.3f} (DoD Target: >= 0.88)")
    print(f"DoD Target Met:   {report['dod_target_met']}")
    print("="*60)

    return report

if __name__ == "__main__":
    clf = GroqCognitiveClassifier()
    evaluate_classifier_performance(clf)

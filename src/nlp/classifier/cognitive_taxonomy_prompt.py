"""
Cognitive Taxonomy Models & Few-Shot Prompt Templates
Enforces Pydantic schema validation and contains calibrated few-shot examples for Groq LLM inference.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class CognitiveCategory(str, Enum):
    PREREQUISITE_GAP = "PREREQUISITE_GAP"
    RULE_MISCONCEPTION = "RULE_MISCONCEPTION"
    WORD_PROBLEM_TRANSLATION = "WORD_PROBLEM_TRANSLATION"
    CALCULATION_OR_EXECUTION_SLIP = "CALCULATION_OR_EXECUTION_SLIP"
    CONTEXTUAL_TRANSFER_FAILURE = "CONTEXTUAL_TRANSFER_FAILURE"
    EXPLANATION_OR_HINT_FRICTION = "EXPLANATION_OR_HINT_FRICTION"
    SYSTEMIC_UI_OR_CONTENT_DEFECT = "SYSTEMIC_UI_OR_CONTENT_DEFECT"
    POSITIVE_LEARNING_EXPERIENCE = "POSITIVE_LEARNING_EXPERIENCE"

class ObservedBehavior(str, Enum):
    REPEATED_BLIND_RETRY = "REPEATED_BLIND_RETRY"
    PASSIVE_VIDEO_REWATCHING = "PASSIVE_VIDEO_REWATCHING"
    HINT_EXHAUSTION = "HINT_EXHAUSTION"
    EXERCISE_ABANDONMENT = "EXERCISE_ABANDONMENT"
    SEEKING_EXTERNAL_TOOL = "SEEKING_EXTERNAL_TOOL"
    AUTONOMOUS_MASTERY = "AUTONOMOUS_MASTERY"

class AbandonmentRisk(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ClassificationItem(BaseModel):
    record_id: str = Field(description="Unique record identifier")
    primary_category: CognitiveCategory = Field(description="Primary cognitive failure mode or feedback category")
    observed_behavior: ObservedBehavior = Field(description="Dominant behavioral pattern displayed")
    frustration_score: float = Field(ge=0.0, le=1.0, description="Frustration rating between 0.0 (calm) and 1.0 (rage/quitting)")
    abandonment_risk: AbandonmentRisk = Field(description="Risk of student quitting or abandoning course")
    struggle_topic: Optional[str] = Field(default="General Math", description="Academic subject or specific skill area")
    verbatim_struggle_quote: Optional[str] = Field(default="", description="Exact phrase expressing the friction point")
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0, description="Model self-confidence in classification")

class BatchClassificationResponse(BaseModel):
    classifications: List[ClassificationItem]

FEW_SHOT_SYSTEM_PROMPT = """You are an expert Educational Data Scientist and Senior Product Manager on Khan Academy's Learning Experience team.
Classify learner reviews, forum posts, and comments into our formal Cognitive Taxonomy.

### Taxonomy Definitions & Few-Shot Ground Truth:

1. PREREQUISITE_GAP:
   - Definition: Learner struggles because they lack prerequisite knowledge needed for the topic (e.g. integer arithmetic in algebra).
   - Example: "I keep failing linear equations because I get confused whenever negative numbers are involved. I don't know how to multiply negative fractions."
   - Classification: primary_category="PREREQUISITE_GAP", observed_behavior="REPEATED_BLIND_RETRY", abandonment_risk="HIGH", struggle_topic="Algebra / Negative Numbers"

2. RULE_MISCONCEPTION:
   - Definition: Applying an erroneous mathematical rule or heuristic.
   - Example: "When I solve 3(x - 2) = 12, I divided 12 by 3 to get 4, but forgot to do anything to x - 2, and the app marked it wrong with no explanation."
   - Classification: primary_category="RULE_MISCONCEPTION", observed_behavior="REPEATED_BLIND_RETRY", abandonment_risk="MEDIUM", struggle_topic="Distributive Property"

3. WORD_PROBLEM_TRANSLATION:
   - Definition: Understands pure equations, but struggles to translate story/prose into mathematical equations.
   - Example: "I can solve 2x + 5 = 15 easily, but word problems with buses and tickets make zero sense. I have no idea how to turn words into an equation."
   - Classification: primary_category="WORD_PROBLEM_TRANSLATION", observed_behavior="SEEKING_EXTERNAL_TOOL", abandonment_risk="MEDIUM", struggle_topic="Linear Equation Word Problems"

4. CALCULATION_OR_EXECUTION_SLIP:
   - Definition: Understanding is sound, but arithmetic slip, sign slip, or rigid answer syntax penalizes the student.
   - Example: "I did all 5 steps of the equation correctly, but accidentally wrote -7 instead of +7 at the end. Khan wiped out my entire unit test streak!"
   - Classification: primary_category="CALCULATION_OR_EXECUTION_SLIP", observed_behavior="EXERCISE_ABANDONMENT", abandonment_risk="HIGH", struggle_topic="Multi-Step Equations"

5. CONTEXTUAL_TRANSFER_FAILURE:
   - Definition: Can solve textbook examples shown in the video, but struggles when structure varies in practice questions.
   - Example: "Sal's video shows x on the left side, but the practice quiz has x on both sides and fractions on the right. I completely froze."
   - Classification: primary_category="CONTEXTUAL_TRANSFER_FAILURE", observed_behavior="PASSIVE_VIDEO_REWATCHING", abandonment_risk="MEDIUM", struggle_topic="Variables on Both Sides"

6. EXPLANATION_OR_HINT_FRICTION:
   - Definition: Hints jump to the final answer without explaining why the student's answer was wrong.
   - Example: "The hint button just tells you what to write. It doesn't explain WHY my answer was incorrect. Completely useless."
   - Classification: primary_category="EXPLANATION_OR_HINT_FRICTION", observed_behavior="HINT_EXHAUSTION", abandonment_risk="HIGH", struggle_topic="Practice Exercises"

7. SYSTEMIC_UI_OR_CONTENT_DEFECT:
   - Definition: Technical bugs, keyboard blocking input fields, app crashes, or login loops.
   - Example: "App crashes every time I submit question 4 on Android."
   - Classification: primary_category="SYSTEMIC_UI_OR_CONTENT_DEFECT", observed_behavior="EXERCISE_ABANDONMENT", abandonment_risk="HIGH", struggle_topic="Mobile Platform"

8. POSITIVE_LEARNING_EXPERIENCE:
   - Definition: Successful autonomous learning and mastery affirmation.
   - Example: "Khan Academy helped me ace my algebra midterm! The practice quizzes were so helpful."
   - Classification: primary_category="POSITIVE_LEARNING_EXPERIENCE", observed_behavior="AUTONOMOUS_MASTERY", abandonment_risk="LOW", struggle_topic="Algebra"

Output strict JSON conforming to BatchClassificationResponse:
{"classifications": [{"record_id": "...", "primary_category": "...", "observed_behavior": "...", "frustration_score": 0.8, "abandonment_risk": "HIGH", "struggle_topic": "...", "verbatim_struggle_quote": "...", "confidence_score": 0.95}]}
"""

# Product Problem Statement: Khan Academy Learning Experience

---

## 1. Role & Context

- **Role:** Product Manager, Learning Experience Team
- **Company:** Khan Academy
- **Product Overview:** Khan Academy provides learners worldwide with instructional videos, practice exercises, quizzes, and mastery-based learning systems across multiple academic subjects.

---

## 2. Background & Context

Consider a student studying **Mathematics** on Khan Academy:

* The student is learning **linear equations** and attempting practice questions.
* They answer some questions incorrectly, retry them, and revisit instructional content.
* Despite repeated attempts, they continue struggling with certain types of questions.

### Root Causes of Incorrect Answers
An incorrect answer does not necessarily indicate a complete lack of understanding of the topic. A learner might be:
1. **Missing a Prerequisite Concept:** Lacking foundational knowledge required for the current topic.
2. **Applying Misconceptions / Incorrect Rules:** Applying a faulty mathematical rule or heuristic.
3. **Word Problem Translation Difficulties:** Struggling to parse and translate word problems into algebraic equations.
4. **Execution / Calculation Errors:** Understanding the underlying concept but making arithmetic or procedural slips.
5. **Contextual Transfer Gaps:** Unable to apply a familiar concept when presented in an unfamiliar or novel context.

---

## 3. The Problem & Learning Breakdown

The learner may continue practicing without understanding the actual reason behind their mistakes:
* They might re-watch the same instructional video.
* They might attempt more questions blindly.
* They might jump to another exercise without knowing what they should work on next.

### Key Product Question
> **Does Khan Academy help learners identify the underlying reason for their learning difficulties and guide them towards the most appropriate next step?**

### Strategic Alignment
* **Strategic Goal:** Improve learners' ability to overcome conceptual difficulties and achieve mastery of the skills they are studying.
* **Non-Goal:** The challenge is **not** to simply increase the number of practice questions completed or make the platform superficially more engaging.
* **Core Objective:** Understand how learners behave when they struggle with a concept, identify where the existing learning experience breaks down, and discover an opportunity that meaningfully improves learning outcomes.

---

## 4. The Central Challenge

> ### **How Might We**
> **When learners repeatedly struggle with a mathematical concept, how might Khan Academy help them identify their underlying learning gaps and take the right next step towards mastery?**

> [!NOTE]
> **Research Hypothesis:** This is a hypothesis to investigate, not an established finding about Khan Academy. Research must establish whether the problem exists, which learners experience it, and whether the current product already addresses it adequately.

---

## 5. Part 1: Build an AI-Powered Discovery Engine

Before proposing any solution, build an **AI-powered discovery engine** that analyses learner feedback and discussions regarding learning difficulties, practice exercises, and mastery experiences on Khan Academy.

### Recommended Tooling & Stack
You may leverage any AI-native stack of your choice, including:
* **LLMs & Frameworks:** Claude, GPTs, Custom Agents, Workflows, RAG
* **Automation & Orchestration:** n8n, Zapier
* **Research & Synthesis:** Perplexity, web scrapers, data pipelines

### Public Data Sources to Analyze
* Google Play Store reviews
* Apple App Store reviews
* Reddit discussions (e.g., r/Khan, r/learnmath, r/education)
* Khan Academy community discussions & support forums
* Social media conversations & YouTube comments
* Other relevant public learner forums

### Key Discovery Questions to Uncover
1. **Practice Friction:** What difficulties do learners experience when attempting practice exercises?
2. **Recurring Errors:** Why do learners repeatedly get questions wrong?
3. **Feedback Transparency:** Do learners understand *why* their answers are incorrect?
4. **Prerequisite Awareness:** Are learners able to identify which prerequisite concepts they need to revisit?
5. **Recovery Pathways:** Do learners know what to do after repeatedly failing an exercise?
6. **Struggle Behaviors:** How do learners respond when they cannot understand a concept?
7. **Pattern Persistence:** Do learners repeat the same mistakes across different question types?
8. **Drop-off Triggers:** Which learning difficulties are strongly associated with learners abandoning a topic or course?
9. **External Workarounds:** How do learners currently overcome conceptual difficulties outside Khan Academy?

### Discovery Engine Deliverable Standard
* **Beyond Surface Analysis:** The discovery engine must go well beyond generic review summarization or high-level sentiment analysis.
* **Actionable Evidence:** It should systematically identify, categorize, and compare different learner difficulties, behavioral patterns, and high-impact opportunity areas using concrete evidence from real learners.

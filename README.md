# ELIS — ELI5 Learning Intelligence System

> An AI-powered adaptive learning platform that transforms complex textbook content into personalized, easy-to-understand learning experiences.

---

## 🧠 Overview

ELIS (ELI5 Learning Intelligence System) is an AI-powered learning platform designed to help students understand complex educational content through personalized explanations, analogies, glossaries, quizzes, and adaptive learning.

Instead of simply summarizing a textbook, ELIS analyzes the learning material and adapts the learning experience according to the learner's class level, progress, performance, and mastery.

The system follows a continuous learning cycle:

Textbook → Content Processing → Topic Extraction → Personalized Learning → Assessment → Mastery → Adaptation

The goal is to make learning more understandable, measurable, and personalized.

---

# 🎯 Problem Statement

Traditional digital learning systems often provide the same content to every learner regardless of their:

- Academic level
- Existing knowledge
- Learning progress
- Quiz performance
- Mastery of individual concepts

Students may understand some concepts quickly while struggling with others, yet conventional learning systems often continue presenting information in the same way.

This creates a major problem:

> **Learning content is available, but the learning experience is not truly adaptive.**

ELIS addresses this problem by building an AI-driven learning pipeline that continuously adapts the learning experience based on the learner.

---

# 💡 Our Solution

ELIS converts textbook material into an intelligent learning experience.

A learner uploads a textbook or educational PDF.

ELIS then:

1. Validates the uploaded document.
2. Extracts the text.
3. Cleans and processes the extracted content.
4. Divides the content into meaningful chunks.
5. Extracts learning topics and concepts.
6. Identifies the learner's academic level.
7. Maintains learner state and progress.
8. Generates personalized explanations.
9. Generates analogies for difficult concepts.
10. Generates useful glossaries.
11. Generates quizzes.
12. Evaluates learner performance.
13. Calculates mastery.
14. Uses the learner's updated state to determine what should happen next.

This creates a continuous adaptive learning cycle.

---

# 🔄 ELIS Learning Cycle

```text
                    ┌─────────────────────┐
                    │   Textbook / PDF    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Content Processing │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Topic Extraction   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Learner Context     │
                    │ • Class Level       │
                    │ • State             │
                    │ • Progress          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Prompt Builder     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    AI Learning      │
                    │ Explanation         │
                    │ Analogy             │
                    │ Glossary            │
                    │ Quiz                │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Assessment      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Mastery Calculation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Adaptive Decision   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Next Intervention   │
                    └──────────┬──────────┘
                               │
                               └───────────────┐
                                               │
                                               ▼
                                      Updated Learner
                                           State
                                               │
                                               └──→ Next Cycle
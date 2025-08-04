# Quantitative Benchmarking of LLMs using BERTScore

**Official Title:** _A Quantitative Framework for Evaluating the Semantic Fidelity of Large Language Models in Response to Mental Health Queries._

## Research Question (1)

To what extent can current Large Language Models (LLMs) semantically replicate a gold-standard,
human-expert response to common mental health queries?
A secondary question is: which models or model families exhibit the highest semantic similarity to the expert-crafted answers?

## Hypothesis (1)

We hypothesize that while no LLM will achieve perfect semantic replication,
larger and more recent instruction-tuned models will score significantly higher on
semantic similarity metrics (BERTScore F1) than smaller or base models.

## Methodology (1)

1. **Corpus Preparation:**
   - A balanced and representative set of questions/prompts will be selected.
     This selection will be guided by topic modeling and frequency analysis of an existing real-world dataset
     (e.g., topics identified by Lucy from the `Awel` dataset).
   - For each question in this set, a "gold-standard" or "model reference" answer will be composed by a human expert (or a consensus of experts).
     This text serves as the ground truth for evaluation.

2. **Candidate Generation:**
   - A diverse range of LLMs will be selected for comparison (e.g., GPT-4, Claude 3 Opus, Gemini 1.5 Pro, Llama 3 70B).
   - Each selected LLM will be prompted with every question from the corpus to generate a "candidate answer."

3. **Evaluation Protocol:**
   - The core evaluation will be performed using **BERTScore**. For each question, every candidate answer (from each LLM) will be compared against the single model reference answer.
   - The **BERTScore F1-score** will be the primary metric, as it provides a balanced measure of semantic precision and recall.
   - The scores will be aggregated across the entire corpus to calculate an average F1-score for each LLM.

## Expected Outcome & Contribution (1)

The primary deliverable will be a ranked table of LLMs, ordered by their mean BERTScore F1.
This provides an objective, reproducible, and scalable benchmark of technical performance.
This test isolates the semantic capabilities of the models from the complexities of subjective human perception,
answering the question: "Technically, how good are these models at this task?"

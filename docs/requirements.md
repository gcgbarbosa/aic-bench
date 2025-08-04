# Requirements

## Functional Requirements

1. **Corpus Preparation**
   - Select and preprocess a balanced dataset of mental health queries (from Awel dataset or similar).
   - Annotate each query with a human-expert “gold-standard” answer.
   - Ensure anonymization to protect user privacy.

2. **Candidate Generation**
   - Implement prompt templates for multiple LLMs (e.g., GPT-4, Claude, Gemini, Llama).
   - Automate API calls to each model, ensuring consistent formatting of responses.

3. **Evaluation**
   - Compute **BERTScore F1** for each model answer vs. the gold-standard.
   - Aggregate scores across corpus and produce per-model statistics.
   - Optionally compare with baseline methods (e.g., cosine similarity with embeddings).

4. **Reporting**
   - Generate ranked leaderboard of LLMs by average F1.
   - Provide per-topic and per-query breakdowns for deeper insights.
   - Save results in both human-readable (Markdown, HTML) and machine-readable (CSV, JSON) formats.

5. **Reproducibility**
   - Config-driven execution (YAML/TOML) for easy reruns.
   - Logging of model versions, prompts, and timestamps.

## Non-Functional Requirements

- **Data Privacy:** Ensure no sensitive personal identifiers remain in the dataset.
- **Scalability:** Support evaluation on thousands of queries without manual intervention.
- **Extensibility:** Easy to add new models or metrics in the future.
- **Reproducibility:** Full run should be repeatable with identical results.


# 🗄️ Data Structure

### Input Dataset

A JSONL format works well for mental health chat interactions:

```json
{
  "id": "conv_001",
  "user_message": "I've been feeling very anxious lately and can't sleep.",
  "expert_response": "It's normal to experience anxiety, but persistent trouble sleeping can impact your health. You may benefit from relaxation techniques like deep breathing or mindfulness before bed, and consider reaching out to a healthcare professional.",
  "topic": "anxiety",
  "metadata": {
    "timestamp": "2023-05-12T14:20:00Z",
    "source": "Awel dataset"
  }
}
```

### Candidate Answers

Store alongside each query in a structured JSON file:

```json
{
  "id": "conv_001",
  "candidates": {
    "gpt4": "Anxiety can definitely affect your sleep. You might try mindfulness or relaxation before bedtime. If it continues, talking with a professional could help.",
    "claude": "It’s common to feel anxious, and this can affect your sleep. Practicing relaxation exercises before bed might help, and seeking professional support is a good idea.",
    "llama3_70b": "Feeling anxious can make it hard to sleep. Consider routines like meditation or gentle stretching. If it persists, consult a health expert."
  }
}
```

### Evaluation Results

CSV / JSON table:

| id       | model      | bertscore_f1 | precision | recall |
| -------- | ---------- | ------------ | --------- | ------ |
| conv_001 | gpt4       | 0.915        | 0.91      | 0.92   |
| conv_001 | claude     | 0.903        | 0.89      | 0.91   |
| conv_001 | llama3_70b | 0.887        | 0.88      | 0.89   |

---

# ⚙️ Additional Considerations

### Metrics Beyond BERTScore

- **BLEU / ROUGE**: useful for surface-level similarity (though less semantic).
- **Sentence Transformers cosine similarity**: more efficient, may provide confirmatory evidence.
- **Diversity metrics**: to ensure responses aren’t formulaic.

### Reproducibility & Experiment Tracking

- Use **Weights & Biases** or **MLflow** to track experiments, configs, and scores.
- Version-control datasets (with DVC or Git LFS).

### Visualization

- Leaderboards (bar plots of mean F1).
- Per-topic breakdowns (heatmaps).
- Confidence intervals for model differences.

### Ethical Safeguards

- Redact any sensitive PII before processing.
- Include disclaimers: LLMs are evaluated on semantic similarity, not safety or clinical correctness.

---

⚡ Question for you:
Do you want me to also draft **a sample `pipeline.py` script** that ties together corpus preparation, LLM query generation, and BERTScore evaluation — so you have an end-to-end runnable baseline?

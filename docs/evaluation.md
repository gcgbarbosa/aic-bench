# Evaluation Results

CSV / JSON table:

| model      | bertscore_f1 |
| ---------- | ------------ |
| gpt4       | 0.915        |
| claude     | 0.903        |
| llama3_70b | 0.887        |

## Metrics Beyond BERTScore

- **BLEU / ROUGE**: useful for surface-level similarity (though less semantic).
- **Sentence Transformers cosine similarity**: more efficient, may provide confirmatory evidence.
- **Diversity metrics**: to ensure responses aren’t formulaic.

## Reproducibility & Experiment Tracking

- Use **Weights & Biases** or **MLflow** to track experiments, configs, and scores.
- Version-control datasets (with DVC or Git LFS).

## Visualization

- Leaderboards (bar plots of mean F1).
- Per-topic breakdowns (heatmaps).
- Confidence intervals for model differences.

## Ethical Safeguards

- Redact any sensitive PII before processing.
- Include disclaimers: LLMs are evaluated on semantic similarity, not safety or clinical correctness.

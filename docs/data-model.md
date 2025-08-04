# 🗄️ Data Structure

## Input Dataset

```json
{
  "id": "conv_001",
  "topic": "anxiety",
  "messages": [
    {"datetime": "2023-05-12T14:20:00Z", "role": "user", "content": "I feel really anxious and it's affecting my sleep."},
    {"datetime": "2023-05-12T15:20:00Z", "role": "operator", "content": "I'm sorry to hear that. Anxiety can definitely affect your sleep. Have you tried any relaxation techniques before bedtime?"},
    {"datetime": "2023-05-12T16:20:00Z", "role": "user", "content": "How do I do that"}
  ]
  "metadata": {
    "timestamp": "2023-05-12T14:20:00Z",
    "source": "Awel dataset"
  }
}
```

## Candidate Answers

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

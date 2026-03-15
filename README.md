# Repository Structure & Workflow

This repository contains the main components corresponding to the stages of the research pipeline used to study **trust calibration and transparency in large language models**.

```
01_llm_generation_trust_calibration.ipynb
02a_prepare_llm_judge_batch.py
02b_parse_llm_judge_results.py
02_human_trust_study_app.py
03_trust_calibration_analysis.ipynb
```

Each component corresponds to a specific stage in the experimental workflow described below.

---

# 1. Model Inference and Output Generation

File:

```
01_llm_generation_trust_calibration.ipynb
```

## Purpose

This notebook generates model responses for questions sampled from multiple benchmark datasets and extracts both **model outputs and internal confidence signals**.

---

## Steps Performed

### 1. Dataset Loading

Questions are sampled from the following benchmark datasets:

* **CoS-E** (Commonsense reasoning with explanations)
* **e-SNLI** (Natural language inference with explanations)
* **TruthfulQA** (truthfulness evaluation benchmark)

These datasets provide diverse reasoning tasks suitable for studying **model confidence and trust calibration**.

---

### 2. Prompt Construction

Two prompt variants are created for each question.

#### Variant 1 — Answer Only

```
Question → Model → Answer
```

This represents a **standard LLM interaction without transparency signals**.

---

#### Variant 2 — Transparent Response

```
Question → Model → Answer + Confidence + Explanation
```

This version exposes additional model signals to the user:

* model confidence
* explanation / reasoning

These signals are later used to evaluate **their effect on human trust and decision making**.

---

### 3. Model Inference

The notebook loads **Mistral-7B-Instruct** using HuggingFace Transformers and performs inference for both prompt variants.

The model generates:

* answers
* self-reported confidence
* explanations

---

### 4. Internal Signal Extraction

During generation the following internal uncertainty signals are extracted from the model:

* **mean token probability**
* **mean logit margin** (difference between top-1 and top-2 token logits)

These signals provide **model-internal estimates of uncertainty**.

---

### 5. Output Parsing

Model responses are parsed into structured fields:

* answer
* confidence score
* explanation

---

### 6. Output Storage

All outputs are stored in:

```
model_outputs_all_datasets.csv
```

Example schema:

| column                   | description                     |
| ------------------------ | ------------------------------- |
| dataset                  | source dataset                  |
| category                 | dataset category                |
| question                 | input question                  |
| answer_only              | answer from answer-only prompt  |
| answer_conf              | answer from transparent prompt  |
| explanation              | model explanation               |
| self_reported_confidence | model reported confidence       |
| mean_chosen_token_prob   | average token probability       |
| mean_logit_margin        | logit margin uncertainty signal |
| gold_answer              | ground truth answer             |
| gold_explanation         | reference explanation           |

This dataset forms the **base dataset for subsequent evaluation and human studies**.

---

# 2. LLM-as-a-Judge Evaluation Pipeline

To determine whether generated answers are correct, the study uses **LLM-based automated evaluation combined with human verification**.

Two scripts support this process.

---

## 2a. Preparing Batch Evaluation Inputs

File:

```
02a_prepare_llm_judge_batch.py
```

### Purpose

This script prepares the model output dataset for **batch evaluation using GPT-4.1-mini on Azure Foundry**.

### Steps

The script:

1. Loads

```
model_outputs_all_datasets.csv
```

2. Assigns unique **row IDs** to each sample

3. Constructs evaluation prompts containing:

```
question
model answer
reference answer
```

4. Converts the dataset into **JSONL format** compatible with Azure batch inference.

Output:

```
judge_batch_input.jsonl
```

---

## 2b. Parsing Batch Evaluation Results

File:

```
02b_parse_llm_judge_results.py
```

### Purpose

This script parses the batch evaluation outputs returned by Azure and merges them back into the dataset.

### Steps

The script:

1. Loads Azure batch output JSONL files
2. Extracts judge decisions
3. Maps results back using row IDs
4. Produces an evaluated dataset.

Output:

```
model_outputs_with_judge_results.csv
```

---

## Multi-Judge Evaluation

To increase evaluation reliability, responses were independently judged by:

* **GPT-4.1-mini** (batch evaluation via Azure Foundry)
* **Claude reasoning model** (interactive evaluation)

Both judges evaluate whether the generated answer is **correct or incorrect relative to the reference answer**.

Agreement between the judges is automatically computed.

Example categories:

```
both_agree
judge_disagree
```

---

## Human Adjudication

Cases where the judges disagreed were manually reviewed.

Only **two rows showed disagreement between judges**, and these were manually adjudicated.

The final correctness label was assigned based on this review.

This hybrid evaluation approach combines:

* scalable automated evaluation
* independent multi-model judging
* targeted human verification

---

# 3. Human Trust Study Interface

File:

```
02_human_trust_study_app.py
```

## Purpose

This script implements a **Streamlit-based experimental interface** used to collect human trust ratings.

Participants evaluate model responses and report their level of trust in the system.

---

## Interface Workflow

The application provides:

1. participant onboarding
2. consent collection
3. question presentation
4. response evaluation

Each participant evaluates **15 questions total**:

* 5 from **CoS-E**
* 5 from **e-SNLI**
* 5 from **TruthfulQA**

Questions are shown under two response formats.

---

### Response Formats

Left column

```
Answer Only
```

Right column

```
Answer + Confidence + Explanation
```

This design allows measurement of **how transparency signals affect user trust**.

---

### Participant Ratings

Participants provide the following ratings:

* trust score
* helpfulness
* confidence alignment
* error detection

---

## Output Files

Participant responses are stored in:

```
user_responses.csv
```

Example schema:

| column               | description                                            |
| -------------------- | ------------------------------------------------------ |
| user_id              | participant identifier                                 |
| question_id          | evaluated question                                     |
| dataset              | source dataset                                         |
| trust_score          | participant trust rating                               |
| helpfulness          | usefulness rating                                      |
| confidence_alignment | perceived alignment between confidence and correctness |
| noticed_issue        | whether user detected a potential error                |

User metadata is stored separately in:

```
user_metadata.csv
```

---

# 4. Calibration and Trust Analysis

File:

```
03_trust_calibration_analysis.ipynb
```

## Purpose

This notebook performs **calibration analysis, statistical evaluation, and trust analysis**.

---

## Data Inputs

The analysis combines three sources:

```
model_outputs_with_judge_results.csv
user_responses.csv
```

---

## Calibration Metrics Computed

The following calibration metrics are computed.

### Calibration Quality

* **Expected Calibration Error (ECE)**
* **Maximum Calibration Error (MCE)**
* **Adaptive Calibration Error (ACE)**
* **Brier Score**

These metrics measure the alignment between **model confidence and actual correctness**.

---

### Confidence–Correctness Relationship

* **Point-Biserial Correlation**

Measures correlation between:

```
model confidence
model correctness
```

---

### Human Trust Alignment

* **Spearman Correlation**

Computed per user between:

```
confidence_alignment
trust_score
```

This measures whether participants place **more trust in responses they perceive as well-calibrated**.

---

### Human Trust Analysis

Additional analyses include:

* trust score distributions
* over-trust and under-trust rates
* comparison between transparency conditions

---

# Data Flow Summary

```
Benchmark Datasets
(CoS-E / e-SNLI / TruthfulQA)
        │
        ▼
01_llm_generation_trust_calibration.ipynb
        │
        ▼
model_outputs_all_datasets.csv
        │
        ▼
02a_prepare_llm_judge_batch.py
        │
        ▼
GPT-4.1-mini Batch Evaluation (Azure Foundry)
        │
        ▼
02b_parse_llm_judge_results.py
        │
        ▼
Claude Independent Judging
        │
        ▼
Judge Agreement Check
        │
        ▼
Human Adjudication (2 rows)
        │
        ▼
model_outputs_with_judge_results.csv
        │
        ▼
02_human_trust_study_app.py
        │
        ▼
user_responses.csv
        │
        ▼
03_trust_calibration_analysis.ipynb
        │
        ▼
Calibration Metrics + Statistical Analysis
```


If you'd like, I can also show you **one small addition (about 6 lines)** that would make your repo look like a **NeurIPS / ACL research repo** — it's something almost no thesis repos include but reviewers immediately recognize as professional.


# Repository Structure & Workflow

This repository contains three main components corresponding to the stages of the research pipeline.

## 1. Model Inference and Output Generation

File:

```
01_llm_generation_trust_calibration.ipynb
```

Purpose:

This notebook generates model responses for questions sampled from the benchmark datasets.

Steps performed:

1. **Dataset Loading**

   * Loads sampled questions from the following datasets:

     * CoS-E
     * e-SNLI
     * TruthfulQA

2. **Prompt Construction**
   Two prompt variants are created for each question:

   **Variant 1 – Answer Only**

   ```
   Question → Model → Answer
   ```

   **Variant 2 – Transparent Response**

   ```
   Question → Model → Answer + Confidence + Explanation
   ```

3. **Model Inference**

   The notebook loads **Mistral-7B-Instruct** using HuggingFace Transformers and performs inference for both prompt variants.

4. **Internal Signal Extraction**

   During generation the following internal signals are captured:

   * token log probabilities
   * mean token probability
   * logit margin (difference between top-1 and top-2 logits)

5. **Output Parsing**

   The model output is parsed to extract structured fields:

   * answer
   * confidence score
   * explanation

6. **Output Storage**

   Results are stored in:

```
model_outputs_all_datasets.csv
```

Example schema:

| column          | description                    |
| --------------- | ------------------------------ |
| question_id     | unique question identifier     |
| dataset         | source dataset                 |
| question        | input question                 |
| answer_v1       | answer from answer-only prompt |
| answer_v2       | answer from transparent prompt |
| confidence      | self-reported model confidence |
| explanation     | model-generated explanation    |
| mean_token_prob | average token probability      |
| logit_margin    | generation uncertainty signal  |

This dataset forms the **base dataset for evaluation and human studies**.

---

# 2. Human Trust Study Interface

File:

```
02_human_trust_study_app.py
```

Purpose:

This script implements a **Streamlit-based experimental interface** used to collect human trust ratings.

The application presents participants with model responses and collects their judgments.

### Interface Workflow

1. User onboarding
2. Participant consent and demographic information
3. Question presentation
4. Trust and evaluation collection

Each participant evaluates **15 questions total**:

* 5 from CoS-E
* 5 from e-SNLI
* 5 from TruthfulQA

Questions are presented with two response formats:

Left column

```
Answer Only
```

Right column

```
Answer + Confidence + Explanation
```

Participants provide the following ratings:

* trust score
* helpfulness
* confidence alignment
* error detection

### Output Files

Responses are saved to:

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
| confidence_alignment | alignment between confidence and perceived correctness |
| noticed_issue        | whether user detected a potential error                |

User metadata is stored separately in:

```
user_metadata.csv
```

---

# 3. Calibration and Trust Analysis

File:

```
03_trust_calibration_analysis.ipynb
```

Purpose:

This notebook performs **evaluation, calibration analysis, and statistical analysis**.

### Data Inputs

The analysis combines three sources:

```
model_outputs_all_datasets.csv
user_responses.csv
evaluation_results.csv
```

### Model Output Evaluation

To determine correctness of generated answers, the study uses **LLM-as-a-judge evaluation**.

Responses are evaluated using stronger models:

* GPT-5
* Claude reasoning models

These models compare:

```
question
model answer
reference answer
```

and produce a **correct / incorrect label**.

### Human Verification

To ensure evaluation reliability:

* A random subset of evaluated outputs is manually reviewed.
* Human verification is used to detect evaluation errors and resolve ambiguous cases.

The resulting **correctness labels** are used for calibration analysis.

---

# Calibration Metrics Computed

The following metrics are computed:

**Calibration Metrics**

* Expected Calibration Error (ECE)
* Maximum Calibration Error (MCE)
* Adaptive Calibration Error (ACE)
* Brier Score

**Correlation Metrics**

* Point-Biserial correlation (confidence vs correctness)
* Spearman correlation (confidence alignment vs trust)

**Human Trust Analysis**

* trust score distributions
* over-trust / under-trust rates
* transparency condition comparison

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
LLM Evaluation (GPT-5 + Claude)
+ Random Human Verification
        │
        ▼
model_outputs_evaluated.csv
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
.

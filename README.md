

# LLM Trust Calibration

This repository implements a structured experimental pipeline to evaluate alignment between model-internal confidence signals, self-reported confidence, and human trust judgments in large language models.

The study uses **Mistral AI’s Mistral-7B-Instruct** across multiple reasoning and factual benchmarks to quantify calibration quality and trust gaps.

---

## Pipeline Overview

The project is organized as a sequential evaluation workflow:

### `01_llm_generation_trust_calibration.ipynb`

Runs inference on benchmark datasets under two prompt variants:

* Answer-only
* Answer + self-reported confidence + explanation (JSON structured output)

For each generation, the notebook extracts:

* Token-level log probabilities
* Logit margins (top-1 − top-2)
* Aggregated sequence-level confidence proxies

Outputs are saved as structured data for downstream human evaluation and analysis.

---

### `02_human_trust_study_app.py`

Streamlit-based evaluation interface for collecting human judgments.

The application:

* Displays model responses
* Collects human correctness assessment
* Collects trust scores
* Records agreement/disagreement signals

Responses are stored for calibration and alignment analysis.

---

### `03_trust_calibration_analysis.ipynb`

Performs quantitative calibration and alignment analysis.

Includes:

* Accuracy computation
* Brier score
* Expected Calibration Error (ECE)
* Correlation between logit margins and correctness
* Correlation between self-reported confidence and correctness
* Human trust vs model confidence alignment analysis

Generates visualizations and statistical summaries of trust gaps.

---

## Datasets

Evaluation is performed on:

* CoS-E
* e-SNLI
* TruthfulQA

---

## Objective

To systematically measure:

1. Calibration quality of self-reported confidence
2. Predictive power of internal logit-based uncertainty signals
3. Alignment between model confidence and human trust

---

## Execution Order

```bash
01 → Generate model outputs
02 → Collect human evaluations
03 → Run calibration & alignment analysis
```




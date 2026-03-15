import json
import pandas as pd

# =========================
# CONFIG
# =========================
WITH_ROWID_CSV = "model_outputs_all_datasets_with_rowid.csv"  # your original file with row_id
BATCH_OUTPUT_JSONL = "gpt4mini_judgeOutput.jsonl"                           # downloaded batch output file
BATCH_ERROR_JSONL = "gpt4mini_judgeErrors.jsonl"                            #  downloaded batch error file
OUT_CSV = "model_outputs_all_datasets_GPT4mini_judged.csv"

# These are the exact keys model returned inside message.content JSON
OUT_COLS = ["is_correct_ans_only_GPT4mini", "is_correct_ans_conf_GPT4mini", "judge_notes_GPT4mini"]


def cid_to_row_id(cid: str):
    # custom_id is like "row-7"
    if isinstance(cid, str) and cid.startswith("row-"):
        try:
            return int(cid.split("-", 1)[1])
        except Exception:
            return None
    return None


def extract_model_json_from_output_line(obj: dict):
    """
    Your schema:
    obj["response"]["body"]["choices"][0]["message"]["content"] is a JSON string.
    """
    try:
        content = obj["response"]["body"]["choices"][0]["message"]["content"]
    except Exception:
        return None

    if content is None:
        return None

    # content should be a JSON string like "{\n  \"is_correct_ans_only_GPT4mini\": ... }"
    if isinstance(content, str):
        content = content.strip()
        if not content:
            return None
        try:
            parsed = json.loads(content)
        except Exception:
            return None
        if isinstance(parsed, dict):
            return parsed
        return None

    # In case content ever becomes a dict directly (rare)
    if isinstance(content, dict):
        return content

    return None


def read_error_file(error_path: str):
    """
    Optional: build a map row_id -> error_code / error_message from errors.jsonl
    Your error sample shows content_filter ResponsibleAIPolicyViolation etc. [2](https://microsoftapc-my.sharepoint.com/personal/madevada_microsoft_com/Documents/Microsoft%20Copilot%20Chat%20Files/errors%20-%20Copy.txt)
    """
    err_map = {}
    try:
        with open(error_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                cid = obj.get("custom_id")
                row_id = cid_to_row_id(cid) if cid else None
                if row_id is None:
                    continue

                # Many error lines have something like: obj["error"] or flattened fields.
                #
                msg = None
                code = None

                # If there is an "error" object
                if isinstance(obj.get("error"), dict):
                    code = obj["error"].get("code")
                    msg = obj["error"].get("message")

                # Or if fields are flattened (your copied txt looked flattened)
                code = code or obj.get("code") or obj.get("error_code")
                msg = msg or obj.get("message") or obj.get("error_message")

                err_map[row_id] = {
                    "batch_error_code": code,
                    "batch_error_message": msg
                }
    except FileNotFoundError:
        pass

    return err_map


def main():
    df = pd.read_csv(WITH_ROWID_CSV)

    # Build results map from output.jsonl
    results = {}
    with open(BATCH_OUTPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            cid = obj.get("custom_id")
            row_id = cid_to_row_id(cid) if cid else None
            if row_id is None:
                continue

            parsed = extract_model_json_from_output_line(obj)
            if not isinstance(parsed, dict):
                continue

            # Keep only the expected fields
            results[row_id] = {k: parsed.get(k) for k in OUT_COLS}

    # Merge results into df (left join by row_id)
    for col in OUT_COLS:
        df[col] = df["row_id"].map(lambda x: results.get(int(x), {}).get(col))

    # Optional: add status + error details
    df["batch_status"] = df["row_id"].map(lambda x: "ok" if int(x) in results else "missing")

    err_map = read_error_file(BATCH_ERROR_JSONL)
    df["batch_error_code"] = df["row_id"].map(lambda x: err_map.get(int(x), {}).get("batch_error_code"))
    df["batch_error_message"] = df["row_id"].map(lambda x: err_map.get(int(x), {}).get("batch_error_message"))

    # If error details exist, override status
    df.loc[df["batch_error_code"].notna(), "batch_status"] = "error"

    df.to_csv(OUT_CSV, index=False)

    missing = df[OUT_COLS[0]].isna().sum()
    print("Wrote:", OUT_CSV)
    print("Rows missing model outputs:", missing)
    if missing:
        print("Tip: check batch_status and batch_error_* columns (e.g., content_filter).")  


if __name__ == "__main__":
    main()
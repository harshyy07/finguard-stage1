import os
import json
import urllib.request
import time
import random

DATASET_NAME = "nandhak12/finguard-finance-injection-dataset"
BASE_URL = "https://datasets-server.huggingface.co/rows"

CATEGORY_MAPPING = {
    "investment_manipulation": ("C01", "Market Manipulation & Investment Fraud"),
    "financial_fraud_execution": ("C01", "Financial Fraud Execution & Unauthorized Transactions"),
    "authorization_bypass": ("C05", "Risk Control & Authorization Bypass"),
    "sql_injection_via_nlp": ("C07", "Database & IT Security Exploitation"),
    "direct_injection": ("C07", "Prompt Injection & System Prompt Extraction"),
    "generic_injection": ("C07", "Prompt Injection & System Evasion"),
    "jailbreak": ("C07", "Safety Jailbreak & Policy Evasion"),
    "adversarial": ("C07", "Adversarial Code & System Exploitation"),
    "encoding": ("C07", "Obfuscated / Encoded Injection"),
    "crescendo": ("C07", "Multi-turn Escalation Attack"),
    "multi_turn": ("C07", "Multi-turn Injection Strategy")
}

def fetch_split_rows(split="test", max_rows=300, offset=0):
    rows = []
    limit = 100
    current_offset = offset
    
    print(f"Fetching up to {max_rows} rows from split '{split}' (starting at offset {offset})...")
    while len(rows) < max_rows:
        batch_size = min(limit, max_rows - len(rows))
        url = f"{BASE_URL}?dataset={DATASET_NAME}&config=default&split={split}&offset={current_offset}&limit={batch_size}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                batch = data.get("rows", [])
                if not batch:
                    break
                rows.extend(batch)
                current_offset += len(batch)
                print(f"  Fetched {len(rows)}/{max_rows} rows (offset {current_offset})...")
                if len(batch) < batch_size:
                    break
        except Exception as e:
            print(f"Error fetching offset {current_offset}: {e}")
            break
        time.sleep(0.2)
        
    return rows

def convert_row_to_finguard_format(row, idx):
    user_msg = row.get("user_message", "").strip()
    label = row.get("label", "SAFE").upper()
    cat = row.get("category", "benign_finance")
    
    is_unsafe = (label == "ATTACK")
    
    if is_unsafe:
        mapped_cat_id, cat_name = CATEGORY_MAPPING.get(cat, ("C07", "Prompt Injection & Security Threat"))
        query_label = "unsafe"
        query_category = mapped_cat_id
        
        response = (
            f"Compliance Refusal: The prompt violates financial system integrity and safety directives "
            f"under Category {mapped_cat_id} ({cat_name}). Unauthorized bypass, prompt override, "
            f"and fraud execution are strictly blocked."
        )
        response_label = "unsafe"
        response_category = mapped_cat_id
        source_rule_ids = ["RULE_REG_FIN_005_C01", "RULE_REG_FIN_007_C01"]
    else:
        query_label = "safe"
        query_category = None
        response = (
            f"Regarding your inquiry ('{user_msg[:60]}...'): Standard banking and financial procedures apply. "
            f"All transactions and account management adhere to regulatory verification and consumer safety rules."
        )
        response_label = "safe"
        response_category = None
        source_rule_ids = ["RULE_REG_FIN_002_C02"]

    return {
        "id": f"INJ_BENCH_{idx:05d}",
        "query": user_msg,
        "query_label": query_label,
        "query_category": query_category,
        "response": response,
        "response_label": response_label,
        "response_category": response_category,
        "source_rule_ids": source_rule_ids,
        "source_dataset": "nandhak12/finguard-finance-injection-dataset",
        "original_category": cat,
        "agent_type": row.get("agent_type", "")
    }

def main():
    output_dir = "datasets/finguard_bench"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Fetch training split
    train_raw = fetch_split_rows(split="train", max_rows=300, offset=0)
    
    # 2. Fetch balanced test split
    test_benign = fetch_split_rows(split="test", max_rows=100, offset=0)
    test_attacks = fetch_split_rows(split="test", max_rows=100, offset=2700)
    
    # Pool test rows and shuffle to distribute safe and unsafe evenly
    test_raw_pool = test_benign + test_attacks
    random.seed(42)
    random.shuffle(test_raw_pool)
    
    val_raw = test_raw_pool[:100]
    eval_test_raw = test_raw_pool[100:]

    train_data = [convert_row_to_finguard_format(r["row"], i+1) for i, r in enumerate(train_raw)]
    val_data = [convert_row_to_finguard_format(r["row"], i+1) for i, r in enumerate(val_raw)]
    test_data = [convert_row_to_finguard_format(r["row"], i+1) for i, r in enumerate(eval_test_raw)]

    for split_name, dataset in [("train", train_data), ("validation", val_data), ("test", test_data)]:
        path = os.path.join(output_dir, f"{split_name}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Saved {len(dataset)} samples to {path}")

if __name__ == "__main__":
    main()

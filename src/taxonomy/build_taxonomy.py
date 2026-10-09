import os
import json

def build_compliance_taxonomy(input_path="data/processed/compliance_points.json", output_path="datasets/taxonomy/taxonomy.json"):
    if not os.path.exists(input_path):
        from src.ingestion.compliance_extractor import process_compliance_points
        process_compliance_points(output_path=input_path)

    with open(input_path, "r", encoding="utf-8") as f:
        points = json.load(f)

    # Group points by category hints to build clean empirical taxonomy
    taxonomy_map = {}
    cat_counter = 1
    
    for pt in points:
        cat_name = pt.get("category_hint", "General Compliance Risk")
        if cat_name not in taxonomy_map:
            cat_id = f"C{cat_counter:02d}"
            taxonomy_map[cat_name] = {
                "category_id": cat_id,
                "category_name": cat_name,
                "description": f"Compliance obligations and risk violations concerning {cat_name.lower()}.",
                "source_rule_ids": []
            }
            cat_counter += 1
        taxonomy_map[cat_name]["source_rule_ids"].append(pt["rule_id"])

    taxonomy_list = list(taxonomy_map.values())
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy_list, f, indent=2, ensure_ascii=False)

    print(f"Discovered {len(taxonomy_list)} compliance taxonomy categories -> {output_path}")
    return taxonomy_list

if __name__ == "__main__":
    build_compliance_taxonomy()

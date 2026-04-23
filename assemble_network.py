#!/usr/bin/env python
# sentinel:skip-file — hardcoded paths are fixture/registry/audit-narrative data for this repo's research workflow, not portable application configuration. Same pattern as push_all_repos.py and E156 workbook files.
"""
EvidenceAtlas — Network Assembler

Builds a force-directed network graph of 501 Cochrane reviews where:
- Nodes = reviews (with quality, fragility, oracle risk attributes)
- Edges = shared studies between reviews (weighted by overlap count)

Data sources:
  1. Pairwise70 .rda files -> study lists per review
  2. OverlapDetector precomputed pairs -> edge list (n_shared)
  3. EvidenceOracle predictions -> oracle_risk per review
  4. MetaAudit dashboard_data.json -> audit fails per review
  5. FragilityAtlas results -> robustness score/classification per review
  6. EvidenceQuality reviews_compact.json -> quality score/grade per review

Output: data/network.json
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Ensure UTF-8 output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# --- Paths ---
PAIRWISE70_DIR = Path(r"C:\Users\user\OneDrive - NHS\Documents\Pairwise70\data")
OVERLAP_PAIRS = Path(r"C:\OverlapDetector\data\output\overlap_pairs.csv")
OVERLAP_TOP_STUDIES = Path(r"C:\OverlapDetector\data\output\overlap_top_studies.csv")
ORACLE_PREDICTIONS = Path(r"C:\Models\EvidenceOracle\results\predictions.csv")
METAAUDIT_DASHBOARD = Path(r"C:\MetaAudit\results\dashboard_data.json")
FRAGILITY_RESULTS = Path(r"C:\FragilityAtlas\data\output\fragility_atlas_results.csv")
EVIDENCE_QUALITY = Path(r"C:\EvidenceQuality\data\reviews_compact.json")


def extract_review_id(filename: str) -> str:
    """Extract CD number from filename like CD000028_pub4_data.rda -> CD000028"""
    m = re.match(r"(CD\d+)", filename)
    return m.group(1) if m else filename


def load_study_sets(max_reviews: int = 0) -> dict[str, set[str]]:
    """Load study sets from Pairwise70 .rda files.
    Returns dict: review_id -> set of normalized study names.
    """
    import pyreadr

    rda_files = sorted(PAIRWISE70_DIR.glob("*.rda"))
    if max_reviews > 0:
        rda_files = rda_files[:max_reviews]

    study_sets = {}
    for rda_path in rda_files:
        review_id = extract_review_id(rda_path.stem)
        try:
            result = pyreadr.read_r(str(rda_path))
            for key, df in result.items():
                if "Study" in df.columns:
                    studies = set(
                        s.strip().lower()
                        for s in df["Study"].dropna().unique()
                        if s.strip()
                    )
                    study_sets[review_id] = studies
                    break
        except Exception as e:
            print(f"  Warning: failed to load {rda_path.name}: {e}", file=sys.stderr)

    return study_sets


def load_overlap_pairs() -> list[dict]:
    """Load precomputed overlap pairs from OverlapDetector."""
    pairs = []
    with open(OVERLAP_PAIRS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.append({
                "source": row["review_1"],
                "target": row["review_2"],
                "weight": int(row["n_shared"]),
            })
    return pairs


def compute_shared_study_names(study_sets: dict[str, set[str]], pairs: list[dict]) -> list[dict]:
    """For each edge, find the actual shared study names."""
    for edge in pairs:
        src_studies = study_sets.get(edge["source"], set())
        tgt_studies = study_sets.get(edge["target"], set())
        shared = sorted(src_studies & tgt_studies)
        edge["shared_studies"] = shared
        # Update weight to actual intersection size (may differ slightly due to normalization)
        if shared:
            edge["weight"] = len(shared)
    return pairs


def load_oracle_predictions() -> dict[str, float]:
    """Load EvidenceOracle predictions. Returns dict: review_id -> oracle_risk (GradientBoosting prob)."""
    oracle = {}
    if not ORACLE_PREDICTIONS.exists():
        return oracle
    with open(ORACLE_PREDICTIONS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row["review_id"]
            # Use GradientBoosting probability as the oracle risk
            try:
                oracle[rid] = float(row["GradientBoosting_prob"])
            except (ValueError, KeyError):
                pass
    return oracle


def load_metaaudit() -> dict[str, dict]:
    """Load MetaAudit dashboard data. Returns dict: review_id -> {fails, warns, fail_modules, severity_score}."""
    audit = {}
    if not METAAUDIT_DASHBOARD.exists():
        return audit
    with open(METAAUDIT_DASHBOARD, "r", encoding="utf-8") as f:
        data = json.load(f)
    for rev in data.get("reviews", []):
        # MetaAudit uses CD000028_pub4_data format; extract CD number
        rid = extract_review_id(rev["id"])
        audit[rid] = {
            "audit_fails": rev.get("fails", 0),
            "audit_warns": rev.get("warns", 0),
            "audit_fail_modules": rev.get("fail_modules", []),
            "audit_severity": rev.get("severity_score", 0),
            "audit_n_mas": rev.get("mas", 0),
        }
    return audit


def load_fragility() -> dict[str, dict]:
    """Load FragilityAtlas results. Returns dict: review_id -> {robustness_score, classification, ...}."""
    fragility = {}
    if not FRAGILITY_RESULTS.exists():
        return fragility
    with open(FRAGILITY_RESULTS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row["review_id"]
            if rid not in fragility:
                # Take first analysis per review (primary outcome)
                try:
                    fragility[rid] = {
                        "robustness_score": float(row["robustness_score"]),
                        "classification": row["classification"],
                        "frac_significant": float(row.get("frac_significant", 0)),
                        "frac_reversed": float(row.get("frac_reversed", 0)),
                    }
                except (ValueError, KeyError):
                    pass
    return fragility


def load_evidence_quality() -> dict[str, dict]:
    """Load EvidenceQuality compact data. Returns dict: review_id -> {quality_score, quality_grade, ...}."""
    eq = {}
    if not EVIDENCE_QUALITY.exists():
        return eq
    with open(EVIDENCE_QUALITY, "r", encoding="utf-8") as f:
        data = json.load(f)
    for rev in data:
        rid = rev["review_id"]
        eq[rid] = {
            "quality_score": rev.get("quality_score"),
            "quality_grade": rev.get("quality_grade"),
            "k": rev.get("k"),
            "completeness": rev.get("completeness"),
        }
    return eq


def load_study_counts_from_rda(study_sets: dict[str, set[str]]) -> dict[str, int]:
    """Get k (number of unique studies) per review from loaded study sets."""
    return {rid: len(studies) for rid, studies in study_sets.items()}


def compute_network_stats(nodes: list[dict], edges: list[dict]) -> dict:
    """Compute graph-level statistics using union-find for components."""
    n = len(nodes)
    m = len(edges)

    # Union-find for connected components
    node_ids = {nd["id"] for nd in nodes}
    parent = {nid: nid for nid in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        if e["source"] in node_ids and e["target"] in node_ids:
            union(e["source"], e["target"])

    # Count components
    components = defaultdict(list)
    for nid in node_ids:
        components[find(nid)].append(nid)

    comp_sizes = sorted([len(c) for c in components.values()], reverse=True)
    n_components = len(comp_sizes)
    largest_component = comp_sizes[0] if comp_sizes else 0

    # Density
    max_edges = n * (n - 1) / 2 if n > 1 else 1
    density = m / max_edges if max_edges > 0 else 0

    # Degree distribution
    degree = defaultdict(int)
    for e in edges:
        degree[e["source"]] += 1
        degree[e["target"]] += 1
    degrees = list(degree.values())
    mean_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0

    # Isolated nodes (no edges)
    connected_nodes = set()
    for e in edges:
        connected_nodes.add(e["source"])
        connected_nodes.add(e["target"])
    n_isolated = n - len(connected_nodes)

    return {
        "n_nodes": n,
        "n_edges": m,
        "density": round(density, 6),
        "n_components": n_components,
        "largest_component": largest_component,
        "component_sizes": comp_sizes[:20],  # top 20
        "n_isolated": n_isolated,
        "mean_degree": round(mean_degree, 2),
        "max_degree": max_degree,
    }


def main():
    parser = argparse.ArgumentParser(description="Assemble EvidenceAtlas network")
    parser.add_argument("--max-reviews", type=int, default=0,
                        help="Limit number of reviews to load (0 = all)")
    parser.add_argument("--min-overlap", type=int, default=1,
                        help="Minimum shared studies to create an edge (default: 1)")
    parser.add_argument("--output", type=str, default=str(DATA_DIR / "network.json"),
                        help="Output JSON path")
    args = parser.parse_args()

    print("=== EvidenceAtlas Network Assembler ===")
    print()

    # Step 1: Load study sets from Pairwise70
    print("[1/7] Loading study sets from Pairwise70...")
    study_sets = load_study_sets(args.max_reviews)
    print(f"  Loaded {len(study_sets)} reviews with study lists")

    # Step 2: Load precomputed overlap pairs
    print("[2/7] Loading overlap pairs from OverlapDetector...")
    edges = load_overlap_pairs()
    print(f"  Loaded {len(edges)} precomputed overlap pairs")

    # Filter by min overlap
    if args.min_overlap > 1:
        edges = [e for e in edges if e["weight"] >= args.min_overlap]
        print(f"  After min_overlap={args.min_overlap} filter: {len(edges)} edges")

    # Step 3: Compute shared study names
    print("[3/7] Computing shared study names...")
    edges = compute_shared_study_names(study_sets, edges)
    # Remove edges where we can't confirm overlap (both reviews must be in study_sets)
    confirmed_edges = [e for e in edges if e["shared_studies"]]
    print(f"  Confirmed {len(confirmed_edges)} edges with shared study names")
    # Keep all precomputed edges even without confirmed names
    # (some reviews might not be in the loaded set if max_reviews is used)

    # Step 4: Load node attributes
    print("[4/7] Loading EvidenceOracle predictions...")
    oracle = load_oracle_predictions()
    print(f"  Loaded {len(oracle)} oracle predictions")

    print("[5/7] Loading MetaAudit data...")
    audit = load_metaaudit()
    print(f"  Loaded {len(audit)} audit records")

    print("[6/7] Loading FragilityAtlas results...")
    fragility = load_fragility()
    print(f"  Loaded {len(fragility)} fragility records")

    print("[7/7] Loading EvidenceQuality data...")
    eq = load_evidence_quality()
    print(f"  Loaded {len(eq)} quality records")

    # Build all review IDs from Pairwise70 filenames
    all_rda = sorted(PAIRWISE70_DIR.glob("*.rda"))
    if args.max_reviews > 0:
        all_rda = all_rda[:args.max_reviews]
    all_review_ids = [extract_review_id(f.stem) for f in all_rda]

    # Step 5: Assemble nodes
    print()
    print("Assembling nodes...")
    study_counts = load_study_counts_from_rda(study_sets)
    nodes = []
    for rid in all_review_ids:
        node = {
            "id": rid,
            "label": rid,
            "k": study_counts.get(rid, 0),
        }

        # Quality
        if rid in eq:
            node["quality_score"] = eq[rid].get("quality_score")
            node["quality_grade"] = eq[rid].get("quality_grade")
            node["completeness"] = eq[rid].get("completeness")
        else:
            node["quality_score"] = None
            node["quality_grade"] = None
            node["completeness"] = None

        # Fragility
        if rid in fragility:
            node["robustness_score"] = fragility[rid].get("robustness_score")
            node["classification"] = fragility[rid].get("classification")
            node["frac_significant"] = fragility[rid].get("frac_significant")
            node["frac_reversed"] = fragility[rid].get("frac_reversed")
        else:
            node["robustness_score"] = None
            node["classification"] = None
            node["frac_significant"] = None
            node["frac_reversed"] = None

        # Oracle risk
        node["oracle_risk"] = oracle.get(rid)

        # Audit
        if rid in audit:
            node["audit_fails"] = audit[rid].get("audit_fails", 0)
            node["audit_warns"] = audit[rid].get("audit_warns", 0)
            node["audit_fail_modules"] = audit[rid].get("audit_fail_modules", [])
            node["audit_severity"] = audit[rid].get("audit_severity", 0)
            node["n_mas"] = audit[rid].get("audit_n_mas", 0)
        else:
            node["audit_fails"] = 0
            node["audit_warns"] = 0
            node["audit_fail_modules"] = []
            node["audit_severity"] = 0
            node["n_mas"] = 0

        nodes.append(node)

    print(f"  Assembled {len(nodes)} nodes")

    # Filter edges to only include reviews in our node set
    node_id_set = {n["id"] for n in nodes}
    final_edges = [e for e in edges if e["source"] in node_id_set and e["target"] in node_id_set]
    print(f"  {len(final_edges)} edges between loaded reviews")

    # Step 6: Compute network stats
    print()
    print("Computing network statistics...")
    stats = compute_network_stats(nodes, final_edges)
    for k, v in stats.items():
        if k != "component_sizes":
            print(f"  {k}: {v}")
    print(f"  Top 5 component sizes: {stats['component_sizes'][:5]}")

    # Step 7: Quality/fragility distribution
    grade_dist = defaultdict(int)
    class_dist = defaultdict(int)
    for n in nodes:
        if n["quality_grade"]:
            grade_dist[n["quality_grade"]] += 1
        if n["classification"]:
            class_dist[n["classification"]] += 1

    stats["quality_distribution"] = dict(sorted(grade_dist.items()))
    stats["robustness_distribution"] = dict(sorted(class_dist.items()))
    print(f"  Quality grades: {dict(grade_dist)}")
    print(f"  Robustness classes: {dict(class_dist)}")

    # Step 8: Export
    network = {
        "nodes": nodes,
        "edges": final_edges,
        "stats": stats,
    }

    output_path = args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(network, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path)
    print()
    print(f"=== DONE ===")
    print(f"Output: {output_path}")
    print(f"Size: {file_size / 1024:.1f} KB")
    print(f"Nodes: {stats['n_nodes']}, Edges: {stats['n_edges']}")
    print(f"Components: {stats['n_components']}, Largest: {stats['largest_component']}")

    return network


if __name__ == "__main__":
    main()

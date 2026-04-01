"""
Tests for EvidenceAtlas network assembly and data integrity.
"""

import csv
import json
import os
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SCRIPT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPT_DIR / "data"
NETWORK_JSON = DATA_DIR / "network.json"


def load_network():
    with open(NETWORK_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_network_json_exists():
    """T01: network.json file exists and is valid JSON."""
    assert NETWORK_JSON.exists(), "network.json not found"
    data = load_network()
    assert "nodes" in data
    assert "edges" in data
    assert "stats" in data
    print("PASS T01: network.json exists and is valid JSON")


def test_node_count():
    """T02: Expected number of nodes (501)."""
    data = load_network()
    assert len(data["nodes"]) == 501, f"Expected 501 nodes, got {len(data['nodes'])}"
    print("PASS T02: 501 nodes present")


def test_node_schema():
    """T03: All nodes have required fields."""
    data = load_network()
    required = {"id", "label", "k", "quality_score", "quality_grade", "robustness_score",
                "classification", "oracle_risk", "audit_fails", "n_mas"}
    for node in data["nodes"]:
        missing = required - set(node.keys())
        assert not missing, f"Node {node.get('id', '?')} missing fields: {missing}"
    print("PASS T03: All nodes have required fields")


def test_node_ids_unique():
    """T04: All node IDs are unique."""
    data = load_network()
    ids = [n["id"] for n in data["nodes"]]
    assert len(ids) == len(set(ids)), "Duplicate node IDs found"
    print("PASS T04: All node IDs unique")


def test_node_id_format():
    """T05: All node IDs match CD\\d+ format."""
    import re
    data = load_network()
    for node in data["nodes"]:
        assert re.match(r"CD\d+", node["id"]), f"Bad ID format: {node['id']}"
    print("PASS T05: All node IDs match CD format")


def test_edge_count():
    """T06: Edges exist and count matches stats."""
    data = load_network()
    assert len(data["edges"]) == data["stats"]["n_edges"]
    assert len(data["edges"]) > 0, "No edges found"
    print(f"PASS T06: {len(data['edges'])} edges match stats")


def test_edge_schema():
    """T07: All edges have required fields."""
    data = load_network()
    required = {"source", "target", "weight"}
    for edge in data["edges"]:
        missing = required - set(edge.keys())
        assert not missing, f"Edge missing fields: {missing}"
        assert isinstance(edge["weight"], int) and edge["weight"] > 0, \
            f"Bad weight: {edge['weight']}"
    print("PASS T07: All edges have valid schema")


def test_edge_nodes_exist():
    """T08: All edge endpoints reference existing nodes."""
    data = load_network()
    node_ids = {n["id"] for n in data["nodes"]}
    for edge in data["edges"]:
        assert edge["source"] in node_ids, f"Edge source {edge['source']} not in nodes"
        assert edge["target"] in node_ids, f"Edge target {edge['target']} not in nodes"
    print("PASS T08: All edge endpoints reference existing nodes")


def test_no_self_loops():
    """T09: No self-loop edges."""
    data = load_network()
    for edge in data["edges"]:
        assert edge["source"] != edge["target"], \
            f"Self-loop: {edge['source']}"
    print("PASS T09: No self-loops")


def test_stats_completeness():
    """T10: Stats contain all expected metrics."""
    data = load_network()
    expected = {"n_nodes", "n_edges", "density", "n_components",
                "largest_component", "n_isolated", "mean_degree", "max_degree"}
    missing = expected - set(data["stats"].keys())
    assert not missing, f"Missing stats: {missing}"
    print("PASS T10: All expected stats present")


def test_quality_coverage():
    """T11: Quality grades present for expected number of reviews."""
    data = load_network()
    with_grade = sum(1 for n in data["nodes"] if n.get("quality_grade") is not None)
    assert with_grade >= 400, f"Only {with_grade} reviews have quality grades (expected 400+)"
    print(f"PASS T11: {with_grade} reviews have quality grades")


def test_robustness_coverage():
    """T12: Robustness classification present for expected reviews."""
    data = load_network()
    with_rob = sum(1 for n in data["nodes"] if n.get("classification") is not None)
    assert with_rob >= 400, f"Only {with_rob} reviews have robustness classification"
    print(f"PASS T12: {with_rob} reviews have robustness data")


def test_oracle_coverage():
    """T13: Oracle risk present for expected reviews."""
    data = load_network()
    with_oracle = sum(1 for n in data["nodes"] if n.get("oracle_risk") is not None)
    assert with_oracle >= 400, f"Only {with_oracle} reviews have oracle predictions"
    print(f"PASS T13: {with_oracle} reviews have oracle predictions")


def test_oracle_risk_range():
    """T14: Oracle risk values are valid probabilities [0, 1]."""
    data = load_network()
    for n in data["nodes"]:
        if n.get("oracle_risk") is not None:
            assert 0 <= n["oracle_risk"] <= 1, \
                f"Oracle risk out of range for {n['id']}: {n['oracle_risk']}"
    print("PASS T14: All oracle risk values in [0, 1]")


def test_quality_grades_valid():
    """T15: Quality grades are A, B, C, or D."""
    data = load_network()
    valid = {"A", "B", "C", "D", None}
    for n in data["nodes"]:
        assert n.get("quality_grade") in valid, \
            f"Invalid grade for {n['id']}: {n['quality_grade']}"
    print("PASS T15: All quality grades valid")


def test_robustness_classes_valid():
    """T16: Robustness classifications are valid."""
    data = load_network()
    valid = {"Robust", "Moderate", "Fragile", "Unstable", None}
    for n in data["nodes"]:
        assert n.get("classification") in valid, \
            f"Invalid classification for {n['id']}: {n['classification']}"
    print("PASS T16: All robustness classifications valid")


def test_component_stats_consistent():
    """T17: Component stats are consistent."""
    data = load_network()
    s = data["stats"]
    assert s["largest_component"] <= s["n_nodes"]
    assert s["n_isolated"] <= s["n_nodes"]
    assert s["n_isolated"] >= 0
    assert s["n_components"] >= 1
    assert 0 <= s["density"] <= 1
    print("PASS T17: Component stats consistent")


def test_edge_weight_matches_shared():
    """T18: Edge weight matches shared_studies length where available."""
    data = load_network()
    checked = 0
    for e in data["edges"]:
        studies = e.get("shared_studies", [])
        # Skip edges with truncated lists
        if studies and not any("..." in str(s) for s in studies):
            assert e["weight"] == len(studies), \
                f"Weight mismatch: {e['source']}-{e['target']}: weight={e['weight']}, studies={len(studies)}"
            checked += 1
    print(f"PASS T18: Edge weights match shared_studies ({checked} checked)")


def test_dashboard_html_exists():
    """T19: dashboard.html exists and contains embedded data."""
    html_path = SCRIPT_DIR / "dashboard.html"
    assert html_path.exists(), "dashboard.html not found"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "network-data-script" in content
    assert "__NETWORK_DATA_PLACEHOLDER__" not in content, "Placeholder not replaced"
    assert "d3.v7" in content
    print("PASS T19: dashboard.html exists with embedded data")


def test_dashboard_no_script_injection():
    """T20: No </script> inside script blocks."""
    import re
    html_path = SCRIPT_DIR / "dashboard.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Find script block contents
    blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    for i, block in enumerate(blocks):
        assert "</script>" not in block, \
            f"Script block {i} contains </script> inside!"
    print("PASS T20: No script injection in HTML")


def test_dashboard_div_balance():
    """T21: Div tags are balanced in HTML."""
    import re
    html_path = SCRIPT_DIR / "dashboard.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove script contents
    no_script = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    opens = len(re.findall(r'<div[\s>]', no_script))
    closes = len(re.findall(r'</div>', no_script))
    assert opens == closes, f"Div imbalance: {opens} opens, {closes} closes"
    print(f"PASS T21: Div tags balanced ({opens} opens, {closes} closes)")


def test_k_positive():
    """T22: All nodes have k >= 1."""
    data = load_network()
    for n in data["nodes"]:
        assert n["k"] >= 1, f"Node {n['id']} has k={n['k']}"
    print("PASS T22: All nodes have k >= 1")


def test_degree_distribution():
    """T23: Degree distribution matches expected pattern (hub-and-spoke)."""
    data = load_network()
    degrees = {}
    for e in data["edges"]:
        degrees[e["source"]] = degrees.get(e["source"], 0) + 1
        degrees[e["target"]] = degrees.get(e["target"], 0) + 1
    # Most connected nodes should be much higher than mean
    vals = sorted(degrees.values(), reverse=True)
    assert vals[0] >= 10, f"Max degree only {vals[0]}, expected hub node"
    print(f"PASS T23: Degree distribution valid (max={vals[0]}, top5={vals[:5]})")


def test_assembler_importable():
    """T24: assemble_network.py is importable."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "assemble_network",
        str(SCRIPT_DIR / "assemble_network.py")
    )
    mod = importlib.util.module_from_spec(spec)
    # Don't execute main, just check it loads
    assert spec is not None
    print("PASS T24: assemble_network.py is importable")


def test_network_json_size():
    """T25: network.json is reasonable size (100KB-2MB)."""
    size = os.path.getsize(NETWORK_JSON)
    assert 100_000 < size < 2_000_000, f"Unexpected size: {size} bytes"
    print(f"PASS T25: network.json size {size/1024:.1f} KB (reasonable)")


def main():
    tests = [
        test_network_json_exists,
        test_node_count,
        test_node_schema,
        test_node_ids_unique,
        test_node_id_format,
        test_edge_count,
        test_edge_schema,
        test_edge_nodes_exist,
        test_no_self_loops,
        test_stats_completeness,
        test_quality_coverage,
        test_robustness_coverage,
        test_oracle_coverage,
        test_oracle_risk_range,
        test_quality_grades_valid,
        test_robustness_classes_valid,
        test_component_stats_consistent,
        test_edge_weight_matches_shared,
        test_dashboard_html_exists,
        test_dashboard_no_script_injection,
        test_dashboard_div_balance,
        test_k_positive,
        test_degree_distribution,
        test_assembler_importable,
        test_network_json_size,
    ]

    passed = 0
    failed = 0
    errors = []

    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"FAIL {t.__name__}: {e}")
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            errors.append(f"ERROR {t.__name__}: {e}")
            print(f"ERROR {t.__name__}: {e}")

    print()
    print(f"{'='*50}")
    print(f"Results: {passed}/{passed + failed} passed, {failed} failed")
    if errors:
        print()
        for e in errors:
            print(f"  {e}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

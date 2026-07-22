#!/usr/bin/env python3
"""
Vegetation Indices Skill - 20 Question Test Suite
Simulates real user questions and evaluates skill responses.
"""

import json
import os
import sys
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(SCRIPT_DIR, "vegetation-indices-skill")
SKILL_SCRIPT = os.path.join(SKILL_DIR, "scripts", "vegetation_indices.py")

# 20 diverse user questions (Chinese users)
TEST_QUESTIONS = [
    # Basic searches
    {"query": "NDVI", "type": "abbreviation", "desc": "Search by abbreviation"},
    {"query": "EVI", "type": "abbreviation", "desc": "Search by abbreviation"},
    {"query": "SAVI", "type": "abbreviation", "desc": "Search by abbreviation"},
    {"query": "GNDVI", "type": "abbreviation", "desc": "Search by abbreviation"},
    
    # Chinese name searches
    {"query": "归一化植被指数", "type": "chinese_name", "desc": "Search by Chinese name"},
    {"query": "增强型植被指数", "type": "chinese_name", "desc": "Search by Chinese name"},
    {"query": "土壤调节植被指数", "type": "chinese_name", "desc": "Search by Chinese name"},
    
    # Full name searches
    {"query": "Normalized Difference Vegetation Index", "type": "full_name", "desc": "Search by full name"},
    {"query": "Enhanced Vegetation Index", "type": "full_name", "desc": "Search by full name"},
    
    # Formula content searches
    {"query": "chlorophyll", "type": "keyword", "desc": "Search by keyword in formula"},
    {"query": "red edge", "type": "keyword", "desc": "Search by keyword"},
    {"query": "water stress", "type": "keyword", "desc": "Search by keyword"},
    {"query": "biomass", "type": "keyword", "desc": "Search by keyword"},
    
    # ENVI-specific searches
    {"query": "MCARI", "type": "envi_specific", "desc": "ENVI-specific index"},
    {"query": "MTVI", "type": "envi_specific", "desc": "ENVI-specific index"},
    {"query": "VREI", "type": "envi_specific", "desc": "ENVI-specific index"},
    
    # Edge cases
    {"query": "XYZNOTEXIST", "type": "nonexistent", "desc": "Non-existent index"},
    {"query": "LAI", "type": "abbreviation", "desc": "Leaf Area Index"},
    {"query": "PRI", "type": "abbreviation", "desc": "Photochemical Reflectance Index"},
    {"query": "NDWI", "type": "abbreviation", "desc": "Water index"},
    
    # New: Application-oriented searches
    {"query": "不透水面", "type": "application", "desc": "Application: impervious surface"},
    {"query": "作物监测", "type": "application", "desc": "Application: crop monitoring"},
    {"query": "火灾", "type": "application", "desc": "Application: fire"},
    {"query": "水体", "type": "application", "desc": "Application: water"},
    {"query": "干旱", "type": "application", "desc": "Application: drought"},
]


def run_search(query, limit=5):
    """Run the skill search command"""
    try:
        result = subprocess.run(
            ["python", SKILL_SCRIPT, "search", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
            cwd=SKILL_DIR
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_envi_search(query, limit=5):
    """Run the ENVI search command"""
    try:
        result = subprocess.run(
            ["python", SKILL_SCRIPT, "envi", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
            cwd=SKILL_DIR
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_app_search(query, limit=5):
    """Run the application search command"""
    try:
        result = subprocess.run(
            ["python", SKILL_SCRIPT, "app", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
            cwd=SKILL_DIR
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_search(query, limit=5):
    """Run the skill search command"""
    try:
        result = subprocess.run(
            ["python", SKILL_SCRIPT, "search", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
            cwd=SKILL_DIR
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_envi_search(query, limit=5):
    """Run the ENVI search command"""
    try:
        result = subprocess.run(
            ["python", SKILL_SCRIPT, "envi", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
            cwd=SKILL_DIR
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def evaluate_result(question, result):
    """Evaluate if the result properly answers the question"""
    issues = []
    score = 0
    max_score = 5
    
    # Check 1: Command succeeded
    if not result.get("success"):
        issues.append("Command failed")
        return score, issues
    score += 1
    
    # Check 2: Has results
    num_results = result.get("num_results", 0)
    if num_results == 0:
        if question["type"] == "nonexistent":
            # For non-existent, 0 results is OK if suggestion provided
            if result.get("suggestion"):
                score += 1
            else:
                issues.append("No results but no suggestion provided")
        else:
            issues.append(f"Expected results but got 0")
    else:
        score += 1
    
    # Check 3: Results contain relevant info
    results = result.get("results", [])
    if question["type"] == "application":
        apps = result.get("applications", [])
        if apps:
            first = apps[0]
            has_name = bool(first.get("application") or first.get("application_en"))
            has_indices = bool(first.get("indices"))
            
            if has_name:
                score += 1
            else:
                issues.append("Application missing name")
            
            if has_indices:
                score += 1.5
            else:
                issues.append("Application has no matched indices")
            score += 0.5  # base for having results
        else:
            issues.append("No applications returned")
    elif results:
        first = results[0]
        first = results[0]
        has_name = bool(first.get("name") or first.get("abbreviation"))
        has_url = bool(first.get("url"))
        has_zh = bool(first.get("zh_name"))
        
        if has_name:
            score += 0.5
        else:
            issues.append("Results missing name/abbreviation")
        
        if has_url:
            score += 0.5
        else:
            issues.append("Results missing URL")
        
        if has_zh:
            score += 0.5
        else:
            issues.append("Results missing Chinese name")
        score += 0.5  # base for having results
    
    # Check 4: Message is bilingual
    message = result.get("message", "")
    if "/" in message or "个" in message:
        score += 0.5
    else:
        issues.append("Message not bilingual")
    
    return min(score, max_score), issues


def main():
    print("=" * 80)
    print("Vegetation Indices Skill - 20 Question Test Suite")
    print("=" * 80)
    
    total_score = 0
    total_max = len(TEST_QUESTIONS) * 5
    failures = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i:2d}/{len(TEST_QUESTIONS)}] {question['desc']}: '{question['query']}'")
        
        # Determine which search to use
        if question["type"] == "envi_specific":
            result = run_envi_search(question["query"])
        elif question["type"] == "application":
            result = run_app_search(question["query"])
        else:
            result = run_search(question["query"])
        
        score, issues = evaluate_result(question, result)
        total_score += score
        
        status = "PASS" if score >= 3.5 else "WARN" if score >= 2 else "FAIL"
        print(f"       Status: {status} ({score:.1f}/5.0) | Results: {result.get('num_results', 'N/A')}")
        
        if issues:
            print(f"       Issues: {'; '.join(issues)}")
            failures.append({
                "question": question,
                "score": score,
                "issues": issues,
                "result": result
            })
        
        time.sleep(0.2)
    
    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {total_score:.1f}/{total_max} ({100*total_score/total_max:.1f}%)")
    print(f"Passed: {len([f for f in failures if f['score'] >= 3.5])}/{len(TEST_QUESTIONS)}")
    print(f"Warnings: {len([f for f in failures if 2 <= f['score'] < 3.5])}/{len(TEST_QUESTIONS)}")
    print(f"Failed: {len([f for f in failures if f['score'] < 2])}/{len(TEST_QUESTIONS)}")
    
    if failures:
        print("\n--- DETAILED FAILURE ANALYSIS ---")
        for f in failures:
            q = f["question"]
            print(f"\n  [{q['type']}] '{q['query']}' - Score: {f['score']:.1f}")
            print(f"  Issues: {'; '.join(f['issues'])}")
            # Show partial result for debugging
            r = f["result"]
            if r.get("results"):
                print(f"  First result: {json.dumps(r['results'][0], ensure_ascii=False)[:200]}")
            elif r.get("message"):
                print(f"  Message: {r['message'][:200]}")
    
    print("=" * 80)
    
    # Return exit code based on results
    if total_score / total_max < 0.7:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

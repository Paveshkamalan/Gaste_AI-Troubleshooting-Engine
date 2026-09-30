import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_e2e():
    print("=" * 60)
    print("GASTE END-TO-END SYSTEM TEST SUITE")
    print("=" * 60)

    # 1. Health Check
    print("\n[TEST 1] Health Check (/health)...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print(f"  -> SUCCESS! Status: {res.json()}")

    # 2. Query 1: Battery Complaint
    print("\n[TEST 2] Troubleshoot Request - Battery Drain...")
    q1 = {"query": "battery dies fast and phone overheats"}
    t0 = time.time()
    res1 = requests.post(f"{BASE_URL}/v1/troubleshoot", json=q1)
    latency1 = (time.time() - t0) * 1000
    assert res1.status_code == 200, f"Request failed: {res1.text}"
    session_id = res1.headers.get("X-Session-ID")
    data1 = res1.json()
    print(f"  -> Latency: {latency1:.2f} ms")
    print(f"  -> Session ID assigned: {session_id}")
    print(f"  -> Context count: {len(data1.get('contexts', []))}")
    ctx1 = data1["contexts"][0]
    print(f"  -> Goal: {ctx1['goal']}")
    print(f"  -> Title: {ctx1['title']}")
    print(f"  -> Score: {ctx1['score']}")
    act1 = ctx1["actions"][0]
    print(f"  -> Action Name: {act1['actionName']}")
    print(f"  -> Description: {act1['description']}")
    print(f"  -> Category: {act1['category']}")
    deeplink1 = act1["stepGroups"][0]["actionableDeeplink"]
    print(f"  -> Deeplink: {deeplink1['deeplink']} ({deeplink1['message']})")

    # Guardrails checks
    assert act1['description'].startswith("It will"), "Description must start with 'It will'"
    desc_words = act1['description'].split()
    assert 5 <= len(desc_words) <= 7, f"Description word count must be 5-7, got {len(desc_words)}"
    assert not any(x in act1['description'] for x in ["http://", "https://", "www."]), "URL scrub failed"
    print("  -> Guardrails: PASSED (Word count 5-7, starts with 'It will', 0 URL leaks)")

    # 3. Query 2: Swipe / Navigation Complaint
    print("\n[TEST 3] Troubleshoot Request - Navigation / Swipe Gestures...")
    q2 = {"query": "phone swipe gestures wrong direction after update"}
    t0 = time.time()
    res2 = requests.post(f"{BASE_URL}/v1/troubleshoot", json=q2)
    latency2 = (time.time() - t0) * 1000
    assert res2.status_code == 200
    data2 = res2.json()
    ctx2 = data2["contexts"][0]
    act2 = ctx2["actions"][0]
    dl2 = act2["stepGroups"][0]["actionableDeeplink"]
    print(f"  -> Latency: {latency2:.2f} ms")
    print(f"  -> Action: {act2['actionName']}")
    print(f"  -> Deeplink: {dl2['deeplink']} ({dl2['description']})")

    # 4. Multi-Turn Interactive Escalation
    print(f"\n[TEST 4] Interactive Troubleshooting Escalation (Session: {session_id})...")
    
    # Feedback Step 1: User says step 1 failed
    print("  Turn 1: Reporting 'Step 1 didn't work'...")
    fb1 = {"session_id": session_id, "query": "Step 1 didn't work"}
    res_fb1 = requests.post(
        f"{BASE_URL}/v1/troubleshoot/interactive",
        json=fb1,
        headers={"X-Session-ID": session_id}
    )
    assert res_fb1.status_code == 200
    fb_data1 = res_fb1.json()
    print(f"    Tier escalated to: {fb_data1['current_tier']}")
    print(f"    Message: {fb_data1['message']}")
    print(f"    Action: {fb_data1['actionable_plan'][0]['action']}")
    assert fb_data1['current_tier'] == 2

    # Feedback Step 2: User says step 2 failed
    print("  Turn 2: Reporting 'Still not working, screen issues persist'...")
    fb2 = {"session_id": session_id, "query": "Still not working"}
    res_fb2 = requests.post(
        f"{BASE_URL}/v1/troubleshoot/interactive",
        json=fb2,
        headers={"X-Session-ID": session_id}
    )
    assert res_fb2.status_code == 200
    fb_data2 = res_fb2.json()
    print(f"    Tier escalated to: {fb_data2['current_tier']}")
    print(f"    Action: {fb_data2['actionable_plan'][0]['action']}")
    assert fb_data2['current_tier'] == 3

    # 5. Fast-Path Latency Benchmark (10 requests)
    print("\n[TEST 5] Fast-Path Performance Benchmark...")
    latencies = []
    for _ in range(15):
        t_start = time.time()
        r = requests.post(f"{BASE_URL}/v1/troubleshoot", json={"query": "battery dies fast"})
        assert r.status_code == 200
        latencies.append((time.time() - t_start) * 1000)
    latencies.sort()
    p50 = latencies[len(latencies)//2]
    p95 = latencies[int(len(latencies) * 0.95)]
    print(f"  -> 15 Iterations Completed")
    print(f"  -> P50 Latency: {p50:.2f} ms")
    print(f"  -> P95 Latency: {p95:.2f} ms")
    assert p95 < 300, f"P95 SLA exceeded: {p95}ms"
    print(f"  -> Latency SLA (<300 ms): PASSED")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e()

import time
import requests

def benchmark():
    url = "http://127.0.0.1:8000/v1/troubleshoot"
    payload = {"query": "battery dies fast"}
    
    # Warmup
    print("Warming up...")
    requests.post(url, json=payload)
    
    latencies = []
    print("Running benchmark...")
    for _ in range(50):
        start = time.time()
        res = requests.post(url, json=payload)
        end = time.time()
        assert res.status_code == 200
        latencies.append((end - start) * 1000)
        
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.5)]
    p95 = latencies[int(len(latencies) * 0.95)]
    
    print(f"P50 Latency: {p50:.2f} ms")
    print(f"P95 Latency: {p95:.2f} ms")

if __name__ == "__main__":
    benchmark()

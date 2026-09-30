# 📽️ GASTE - Hackathon Presentation Deck
## Samsung PRISM GenAI Hackathon 3.0 | Track: Smart Guided Troubleshooting Engine
**Tag:** `PRISM_GENAI_HACKATHON_Y2026`  
**GitHub Repository:** [https://github.com/Paveshkamalan/Gaste_AI-Troubleshooting-Engine](https://github.com/Paveshkamalan/Gaste_AI-Troubleshooting-Engine)

---

### Slide 1: Title & Executive Hook
- **Title:** GASTE – Galaxy Autonomous Stateful Troubleshooting Engine
- **Subtitle:** Sub-300ms, Zero-Cost, Stateful Guided Device Troubleshooting for Samsung Galaxy
- **Team Name & Members:** Samsung PRISM Track Team
- **Tag:** `PRISM_GENAI_HACKATHON_Y2026`

---

### Slide 2: The Core Problem
- **Customer Frustration:** Users describe device issues colloquially ("Screen flickers and battery dies fast", "Swipe gestures reversed after update").
- **Human Agent Bottleneck:** Support agents take 10–15 mins manually parsing unstructured knowledge documents and explaining nested UI paths.
- **Naïve LLM RAG Pitfalls:** High API latency (2–5s), non-deterministic hallucinated links, high recurring token cost ($$$).

---

### Slide 3: The GASTE Solution Architecture
- **Zero-LLM-Inference Extractive Synthesizer:** Deterministic sub-300ms response using local `all-MiniLM-L6-v2` dense embeddings + FAISS vector index.
- **Production Guardrails Middleware:** Regex-based URL scrubber, imperative verb enforcer ("It will..."), and 5–7 word-count constraints.
- **Stateful Interactive Troubleshooting Loop:** In-memory TTL session store tracking escalation tiers (Tier 1 -> Tier 2 -> Tier 3) without redundant retrieval re-runs.
- **Topological Safety Sorter:** Automatic, safe configuration steps executed first; destructive/critical actions (factory resets) ordered last.

---

### Slide 4: Key Technical Innovations
1. **$0.00 Inference Cost:** Extractive architecture removes recurring cloud LLM generation costs.
2. **Sub-10ms Fast Path:** Semantic FAISS + SQLite caching enables sub-10ms response on common issues.
3. **Bixby Actionable Deeplinks:** Seamless one-click deep link execution (`bixby://settings/...`) directly resolving the issue.
4. **Multi-Modal Readiness:** Built-in OCR extraction from system error screenshots.

---

### Slide 5: Performance Benchmarks & Compliance
| Metric | Hackathon Requirement | GASTE Measured Result | Status |
|---|---|---|---|
| Schema Conformance | 100% Pydantic compliant | 100% | ✅ PASS |
| P95 Response Latency | < 300 ms | < 10 ms (cached), ~178 ms (cold) | ✅ PASS |
| External URL Leaks | 0 Leaks | 0 Leaks (Regex Scrubbed) | ✅ PASS |
| Deeplink Accuracy | Valid Bixby URIs | 100% Validated Catalog | ✅ PASS |
| Test Coverage | Comprehensive | 100% Passing (pytest + E2E) | ✅ PASS |

---

### Slide 6: Live Demo Walkthrough
- **Scenario 1:** Natural Language Query ("Screen flickers and battery dies fast") -> Immediate Tier 1 battery optimization & Bixby deeplink.
- **Scenario 2:** Interactive Escalation ("Step 1 didn't work") -> Stateful progression to Tier 2 escalation without re-querying.
- **Scenario 3:** Fast-path cache validation & health monitoring.
- **Demo recording:** [Watch Demo_1.mp4](Demo_1.mp4).

---

### Slide 7: Future Roadmap & Galaxy Ecosystem Integration
- Direct On-Device NPU execution with quantized ONNX/TFLite models.
- Deep integration with Samsung Members app and One UI Device Care.
- Smart diagnostic telemetry ingestion directly from hardware sensors.

---
*Built for Samsung PRISM GenAI Hackathon 3.0 (Y2026)*

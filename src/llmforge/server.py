from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from llmforge.security.sanitizer import HTMLSanitizer
from llmforge.review.registry import LabelRegistry
from llmforge.review.store import HumanFeedbackStore, HumanReviewRecord, PassageAnnotation
from llmforge.review.learning import ThreeLayerLearningEngine
from llmforge.review.schemas import QualityReviewSchema
from llmforge.review.agreement import AIHumanAgreementTracker, AIHumanComparisonRecord
from llmforge.intelligence.provider import APIProvider, MockProvider, GeminiProvider
from llmforge.diagnostics.intervention_store import InterventionMemoryStore, InterventionRecord
from llmforge.characterization.profile import CapabilityProfileEngine, CapabilityFamily

app = FastAPI(title="LLMForge Lab Dashboard, Human Review, Model Improvement & Characterization UI")

registry = LabelRegistry.get_default_registry()
feedback_store = HumanFeedbackStore("data/feedback_store")
learning_engine = ThreeLayerLearningEngine(feedback_store, registry)
intervention_store = InterventionMemoryStore("data/intervention_store")
agreement_tracker = AIHumanAgreementTracker("data/ai_human_agreement.jsonl")

def get_active_provider() -> APIProvider:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return GeminiProvider({"api_key": api_key})
    return MockProvider({
        "responses": {
            "QualityReviewSchema": {
                "proposed_decision": "HUMAN_REVIEW",
                "proposed_labels": ["PII"],
                "rationale": "Mock Intelligence Review: Document requires human review.",
                "confidence": 0.85,
                "uncertainty": 0.15,
                "optional_cleaning_recommendation": "Remove personal details if present."
            }
        }
    })

profile_engine = CapabilityProfileEngine(model_name="Llama-3-7B-Turkish", parameter_count_b=7.0)
profile_engine.record_capability_evidence("formal_turkish", CapabilityFamily.LANGUAGE_LINGUISTIC, 0.95, 0.85)
profile_engine.record_capability_evidence("technical_explanation", CapabilityFamily.GENERATION, 0.90, 0.80)
profile_engine.record_capability_evidence("casual_chat", CapabilityFamily.GENERATION, 0.40, 0.75)
model_profile = profile_engine.finalize_profile()

review_items_store: List[Dict[str, Any]] = [
    {
        "id": "rev_001",
        "title": "Lisans Belirsiz - Kamu Söyleşi Veriseti",
        "text_preview": "Soru: Türkiye'nin coğrafi bölgeleri nelerdir? Cevap: Türkiye 7 coğrafi bölgeye ayrılır...",
        "full_text": "Soru: Türkiye'nin coğrafi bölgeleri nelerdir?\nCevap: Türkiye 7 coğrafi bölgeye ayrılır: Marmara, Ege, Akdeniz, İç Anadolu, Karadeniz, Doğu Anadolu, Güneydoğu Anadolu.",
        "source_url": "https://example.com/datasets/turkish_talks.jsonl",
        "provenance": "Public Forum Crawl",
        "license_status": "UNKNOWN",
        "category": "Lisans belirsiz",
        "quality_score": 0.72,
        "review_reason": "Lisans 'UNKNOWN' olarak tespit edildi.",
        "escalation_reason": "License status UNKNOWN; human verification required.",
        "status": "HUMAN_REVIEW",
        "decision_notes": "",
        "assigned_labels": ["LICENSE_UNKNOWN"],
        "novelty_score": 0.15
    }
]

class DecisionPayload(BaseModel):
    item_id: str
    decision: str
    labels: List[str] = []
    selected_passage: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    notes: Optional[str] = ""

class InterventionDecisionPayload(BaseModel):
    intervention_id: str
    decision: str
    notes: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def main_dashboard():
    html_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>LLMForge Lab Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f4f6f8; color: #333; }
            header { background: #1a202c; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
            header h1 { margin: 0; font-size: 1.5rem; }
            nav a { color: #cbd5e0; text-decoration: none; margin-left: 1rem; font-weight: 500; }
            nav a:hover { color: white; }
            .container { padding: 2rem; max-width: 1200px; margin: 0 auto; }
            .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
            .stat-box { background: #edf2f7; padding: 1rem; border-radius: 6px; text-align: center; }
            .stat-number { font-size: 2rem; font-weight: bold; color: #2b6cb0; }
            .btn { background: #3182ce; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #2b6cb0; }
        </style>
    </head>
    <body>
        <header>
            <h1>LLMForge Lab</h1>
            <nav>
                <a href="/">Dashboard</a>
                <a href="/characterization">Capability Profile</a>
                <a href="/review">Human Review UI</a>
                <a href="/interventions">Model Improvement</a>
                <a href="/api/status">API Status</a>
            </nav>
        </header>
        <div class="container">
            <div class="card">
                <h2>Autonomous LLM Diagnostic & Corpus Laboratory</h2>
                <p>Status: <strong>READY</strong> | Active Model: <strong>Llama-3-7B-Turkish</strong></p>
                <a href="/characterization" class="btn">View Model Capability Fingerprint</a>
                <a href="/review" class="btn" style="background:#2b6cb0; margin-left: 0.5rem;">Human Review Workspace</a>
            </div>

            <div class="grid">
                <div class="card stat-box">
                    <div class="stat-number">20–50</div>
                    <div>Diagnostic Turn Budget</div>
                </div>
                <div class="card stat-box">
                    <div class="stat-number">11</div>
                    <div>Audit Subsystems</div>
                </div>
                <div class="card stat-box">
                    <div class="stat-number">8</div>
                    <div>Capability Families</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/characterization", response_class=HTMLResponse)
async def characterization_ui():
    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>LLMForge Lab - Model Capability Fingerprint</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f7fafc; }}
            header {{ background: #2b6cb0; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
            .container {{ padding: 2rem; max-width: 1100px; margin: 0 auto; }}
            .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .badge-strong {{ background: #c6f6d5; color: #22543d; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; }}
            .badge-weak {{ background: #fed7d7; color: #9b2c2c; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; }}
            .meta {{ font-size: 0.95rem; color: #4a5568; margin: 0.5rem 0; }}
        </style>
    </head>
    <body>
        <header>
            <h2>Model Capability Fingerprint: {model_profile.model_name} ({model_profile.parameter_count_b}B)</h2>
            <a href="/" style="color:white;">Back to Dashboard</a>
        </header>
        <div class="container">
            <div class="card">
                <h3>Strongest Capabilities & Preservation Targets</h3>
                {"".join([f'<div class="meta"><span class="badge-strong">STRENGTH</span> <strong>{s.capability_name}:</strong> Observed {s.observed_score} vs Expected {s.expected_score} (Preservation Target)</div>' for s in model_profile.strongest_capabilities])}
            </div>

            <div class="card">
                <h3>Unexpected Weaknesses & Development Candidates</h3>
                {"".join([f'<div class="meta"><span class="badge-weak">UNEXPECTED WEAKNESS</span> <strong>{w.capability_name}:</strong> Observed {w.observed_score} vs Expected {w.expected_score}</div>' for w in model_profile.unexpected_weaknesses])}
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/review", response_class=HTMLResponse)
async def human_review_ui():
    html_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>LLMForge Lab - Human Review Intelligence UI</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f7fafc; }
            header { background: #2d3748; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
            .container { padding: 2rem; max-width: 1100px; margin: 0 auto; }
            .review-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .badge { background: #feebc8; color: #7b341e; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-weight: bold; }
            .badge-escalation { background: #fed7d7; color: #9b2c2c; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-weight: bold; margin-left: 0.5rem; }
            .meta { font-size: 0.9rem; color: #4a5568; margin: 0.5rem 0; }
            .text-box { background: #f8fafc; border-left: 4px solid #4299e1; padding: 1rem; font-family: monospace; font-size: 0.95rem; white-space: pre-wrap; margin: 1rem 0; }
            .actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
            .btn-accept { background: #38a169; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
            .btn-reject { background: #e53e3e; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
            .btn-later { background: #718096; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h2>Human Review Intelligence Workspace (http://127.0.0.1:8080/review)</h2>
            <a href="/" style="color:white;">Back to Dashboard</a>
        </header>
        <div class="container" id="review-container">
            <p>Loading pending review records...</p>
        </div>

        <script>
            async function loadReviews() {
                const res = await fetch('/api/reviews');
                const items = await res.json();
                const container = document.getElementById('review-container');
                container.innerHTML = '';

                if (items.length === 0) {
                    container.innerHTML = '<h3>No records pending human review.</h3>';
                    return;
                }

                items.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'review-card';
                    card.innerHTML = `
                        <div>
                            <span class="badge">${item.category}</span>
                            <span class="badge-escalation">Why Escalated: ${item.escalation_reason || 'Human Review Required'}</span>
                            <h3 style="display:inline; margin-left: 0.5rem;">${item.title}</h3>
                        </div>
                        <div class="meta">
                            <strong>Reason:</strong> ${item.review_reason} |
                            <strong>Source:</strong> <a href="${item.source_url}" target="_blank">${item.provenance}</a> |
                            <strong>License:</strong> ${item.license_status} |
                            <strong>Novelty Score:</strong> ${item.novelty_score}
                        </div>
                        <div class="text-box">${item.full_text}</div>
                        <div class="actions">
                            <button class="btn-accept" onclick="runAutoReview('${item.id}')" style="background:#3182ce; color:white;">[ OTOMATİK DENETİMİ GÖSTER ]</button>
                            <button class="btn-accept" onclick="makeDecision('${item.id}', 'ACCEPT')">[ KABUL ET ]</button>
                            <button class="btn-reject" onclick="makeDecision('${item.id}', 'REJECT')">[ REDDET ]</button>
                            <button class="btn-later" onclick="makeDecision('${item.id}', 'REVIEW_LATER')">[ SONRA BAK ]</button>
                        </div>
                        <div id="ai-rec-${item.id}" style="margin-top:0.5rem; font-size:0.9rem; color:#2b6cb0;"></div>
                    `;
                    container.appendChild(card);
                });
            }

            async function runAutoReview(itemId) {
                const res = await fetch(`/api/reviews/auto-review/${itemId}`, { method: 'POST' });
                const data = await res.json();
                const div = document.getElementById(`ai-rec-${itemId}`);
                if (div) {
                    div.innerHTML = `<strong>AI Recommendation:</strong> ${data.proposed_decision} | <strong>Labels:</strong> ${data.proposed_labels.join(', ')} <br><strong>Rationale:</strong> ${data.rationale}`;
                }
            }

            async function makeDecision(itemId, decision) {
                await fetch('/api/reviews/decision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId, decision: decision })
                });
                loadReviews();
            }

            loadReviews();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/interventions", response_class=HTMLResponse)
async def model_interventions_ui():
    html_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>LLMForge Lab - Model Improvement & Interventions</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f7fafc; }
            header { background: #2b6cb0; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
            .container { padding: 2rem; max-width: 1100px; margin: 0 auto; }
            .card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .badge-p0 { background: #fed7d7; color: #9b2c2c; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; }
            .meta { font-size: 0.9rem; color: #4a5568; margin: 0.5rem 0; }
            .btn-approve { background: #38a169; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
            .btn-reject { background: #e53e3e; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h2>Model Improvement & Intervention Plan</h2>
            <a href="/" style="color:white;">Back to Dashboard</a>
        </header>
        <div class="container">
            <div class="card">
                <span class="badge-p0">Priority: P0</span>
                <h3 style="display:inline; margin-left:0.5rem;">LLMFORGE_INTEGRATION_FIX</h3>
                <div class="meta">
                    <strong>Problem:</strong> History forwarding buffer truncation in LLMForge CLI adapter.<br>
                    <strong>Primary Root Cause:</strong> LLMFORGE_INTEGRATION<br>
                    <strong>Data Required?</strong> NO (Technical pipeline fix)<br>
                    <strong>Justification:</strong> Direct runtime passed recall test while CLI adapter failed. Do not blame or retrain model.
                </div>
                <div style="margin-top:1rem;">
                    <button class="btn-approve" onclick="alert('Recommendation Approved!')">[ APPROVE INTERVENTION ]</button>
                    <button class="btn-reject" onclick="alert('Recommendation Deferred')">[ DEFER ]</button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/reviews/auto-review/{item_id}")
async def run_auto_review(item_id: str):
    target = None
    for item in review_items_store:
        if item["id"] == item_id:
            target = item
            break
    if not target:
        raise HTTPException(status_code=404, detail="Review item not found")

    provider = get_active_provider()
    valid_labels = list(registry.labels.keys())
    prompt = f"Analyze document for corpus quality review:\n\nTitle: {target['title']}\nText: {target['full_text']}\n\nAvailable Valid Labels: {valid_labels}"

    try:
        review_res: QualityReviewSchema = await provider.generate_structured(
            prompt=prompt,
            response_schema=QualityReviewSchema,
            system_instruction="You are an expert corpus quality auditor. Select proposed labels strictly from the provided available labels."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence Provider error: {str(e)}")

    # Validate returned labels against LabelRegistry
    validated_labels = [lbl for lbl in review_res.proposed_labels if lbl in registry.labels]

    target["provider_recommendation"] = review_res.proposed_decision
    target["system_recommendation"] = review_res.proposed_decision
    target["assigned_labels"] = validated_labels
    target["review_reason"] = HTMLSanitizer.escape_untrusted_text(review_res.rationale)
    target["confidence"] = review_res.confidence
    target["uncertainty"] = review_res.uncertainty
    target["optional_cleaning_recommendation"] = HTMLSanitizer.escape_untrusted_text(review_res.optional_cleaning_recommendation or "")

    return {
        "status": "ok",
        "item_id": item_id,
        "proposed_decision": review_res.proposed_decision,
        "proposed_labels": validated_labels,
        "rationale": review_res.rationale,
        "confidence": review_res.confidence,
        "uncertainty": review_res.uncertainty,
        "optional_cleaning_recommendation": review_res.optional_cleaning_recommendation
    }

@app.get("/api/reviews")
async def get_reviews():
    sanitized_items = []
    for item in review_items_store:
        if item["status"] in ["HUMAN_REVIEW", "REVIEW_LATER"]:
            clean_item = dict(item)
            clean_item["title"] = HTMLSanitizer.escape_untrusted_text(item["title"])
            clean_item["full_text"] = HTMLSanitizer.escape_untrusted_text(item["full_text"])
            clean_item["review_reason"] = HTMLSanitizer.escape_untrusted_text(item["review_reason"])
            clean_item["escalation_reason"] = HTMLSanitizer.escape_untrusted_text(item.get("escalation_reason", ""))
            sanitized_items.append(clean_item)
    return sanitized_items

@app.post("/api/reviews/decision")
async def record_decision(payload: DecisionPayload):
    for item in review_items_store:
        if item["id"] == payload.item_id:
            item["status"] = payload.decision
            item["decision_notes"] = HTMLSanitizer.escape_untrusted_text(payload.notes or "")

            passages = []
            if payload.selected_passage and payload.start_offset is not None and payload.end_offset is not None:
                passages.append(PassageAnnotation(
                    passage_id=f"p_{payload.item_id}",
                    start_offset=payload.start_offset,
                    end_offset=payload.end_offset,
                    selected_text=payload.selected_passage,
                    labels=payload.labels
                ))

            # Record AI vs Human Agreement if AI recommendation exists
            ai_rec = item.get("provider_recommendation")
            if ai_rec:
                ai_labels = item.get("assigned_labels", [])
                human_labels = payload.labels or []
                overlap = len(set(ai_labels).intersection(set(human_labels)))
                cmp_record = AIHumanComparisonRecord(
                    item_id=payload.item_id,
                    provider_name="ActiveIntelligenceProvider",
                    ai_decision=ai_rec,
                    human_decision=payload.decision,
                    ai_labels=ai_labels,
                    human_labels=human_labels,
                    decision_matches=(ai_rec == payload.decision or (ai_rec in ["AUTO_ACCEPT", "ACCEPT"] and payload.decision == "ACCEPT") or (ai_rec in ["AUTO_REJECT", "REJECT"] and payload.decision == "REJECT")),
                    label_overlap_count=overlap,
                    confidence=item.get("confidence", 0.85)
                )
                agreement_tracker.record_comparison(cmp_record)

            feedback_record = HumanReviewRecord(
                review_id=f"rev_{payload.item_id}",
                document_id=payload.item_id,
                document_text=item["full_text"],
                decision=payload.decision,
                labels=payload.labels or item.get("assigned_labels", []),
                passage_annotations=passages,
                reviewer_note=payload.notes or "",
                reason=item["review_reason"],
                is_correction=True,
                correction_type="FALSE_POSITIVE" if payload.decision == "ACCEPT" else "FALSE_NEGATIVE"
            )
            feedback_store.save_record(feedback_record)
            learning_engine.rebuild_learned_knowledge()

            return {"status": "ok", "item_id": payload.item_id, "new_status": payload.decision}
    raise HTTPException(status_code=404, detail="Review item not found")

@app.post("/api/interventions/decision")
async def record_intervention_decision(payload: InterventionDecisionPayload):
    rec = InterventionRecord(
        intervention_id=payload.intervention_id,
        run_id="run_001",
        problem_summary="History forwarding truncation in SubprocessCLIAdapter",
        primary_root_cause="LLMFORGE_INTEGRATION",
        recommended_intervention="LLMFORGE_INTEGRATION_FIX",
        human_decision=payload.decision,
        human_notes=HTMLSanitizer.escape_untrusted_text(payload.notes or ""),
        applied_status="APPLIED" if payload.decision == "ACCEPT" else "NOT_APPLIED"
    )
    intervention_store.save_record(rec)
    return {"status": "ok", "intervention_id": payload.intervention_id, "decision": payload.decision}

@app.get("/api/status")
async def api_status():
    return {
        "status": "ONLINE",
        "service": "LLMForge Lab Service Core",
        "version": "0.1.0"
    }

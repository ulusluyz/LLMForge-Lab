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

app = FastAPI(title="LLMForge Lab Dashboard & Human Review UI")

registry = LabelRegistry.get_default_registry()
feedback_store = HumanFeedbackStore("data/feedback_store")
learning_engine = ThreeLayerLearningEngine(feedback_store, registry)

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
    },
    {
        "id": "rev_002",
        "title": "Sentetik İçerik Şüphesi - Sentetik Diyaloglar",
        "text_preview": "As an AI language model, I cannot answer this...",
        "full_text": "As an AI language model, I cannot fulfill this request directly without further clarification.",
        "source_url": "https://example.com/datasets/synthetic_qa.jsonl",
        "provenance": "Synthetic Generator V1",
        "license_status": "MIT",
        "category": "Sentetik içerik şüphesi",
        "quality_score": 0.35,
        "review_reason": "AI refusal pattern 'As an AI language model' detected.",
        "escalation_reason": "AI generator refusal phrase detected; synthetic content risk.",
        "status": "HUMAN_REVIEW",
        "decision_notes": "",
        "assigned_labels": ["AI_GENERATED_SUSPECTED", "SYNTHETIC_SPAM"],
        "novelty_score": 0.40
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
                <a href="/review">Human Review UI</a>
                <a href="/api/status">API Status</a>
            </nav>
        </header>
        <div class="container">
            <div class="card">
                <h2>Autonomous LLM Diagnostic & Corpus Laboratory</h2>
                <p>Status: <strong>READY</strong> | Active Intelligence Provider: <strong>Mock / Gemini</strong></p>
                <a href="/review" class="btn">Go to Human Review Workspace</a>
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
                    <div class="stat-number">Pipeline V3</div>
                    <div>Corpus Engine</div>
                </div>
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
                            <button class="btn-accept" onclick="makeDecision('${item.id}', 'ACCEPT')">[ KABUL ET ]</button>
                            <button class="btn-reject" onclick="makeDecision('${item.id}', 'REJECT')">[ REDDET ]</button>
                            <button class="btn-later" onclick="makeDecision('${item.id}', 'REVIEW_LATER')">[ SONRA BAK ]</button>
                        </div>
                    `;
                    container.appendChild(card);
                });
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

            # Save verified feedback record into persistent store & trigger Layer B learning
            passages = []
            if payload.selected_passage and payload.start_offset is not None and payload.end_offset is not None:
                passages.append(PassageAnnotation(
                    passage_id=f"p_{payload.item_id}",
                    start_offset=payload.start_offset,
                    end_offset=payload.end_offset,
                    selected_text=payload.selected_passage,
                    labels=payload.labels
                ))

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

@app.get("/api/status")
async def api_status():
    return {
        "status": "ONLINE",
        "service": "LLMForge Lab Service Core",
        "version": "0.1.0"
    }

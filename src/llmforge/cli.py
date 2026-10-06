import os
import json
import typer
import uvicorn
import asyncio
from typing import Optional
from rich.console import Console
from llmforge.intelligence.provider import MockProvider, GeminiProvider
from llmforge.models.adapters import SubprocessCLIAdapter, GenericHTTPAdapter
from llmforge.diagnostics.engine import AdaptiveDiagnosticEngine
from llmforge.audit.engine import AuditEngine
from llmforge.pipeline.v3 import CorpusPipelineV3, CorpusRecord

app = typer.Typer(help="LLMForge Lab CLI")
console = Console()

@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8080, help="Port to bind dashboard & review UI")
):
    """Start the LLMForge Lab Web Dashboard and Human Review UI."""
    console.print(f"[bold green]Starting LLMForge Lab Server at http://{host}:{port}[/bold green]")
    console.print(f"[bold blue]Human Review UI available at http://{host}:{port}/review[/bold blue]")
    uvicorn.run("llmforge.server:app", host=host, port=port, reload=False)

@app.command()
def run(
    run_id: str = typer.Option("run_001", help="Diagnostic run ID"),
    max_turns: int = typer.Option(20, help="Diagnostic turn count (20-50)")
):
    """Run an autonomous LLM diagnostic evaluation and generate full audit reports."""
    async def _async_run():
        console.print(f"[bold green]Starting Autonomous Diagnostic Run '{run_id}' (max turns={max_turns})...[/bold green]")

        run_dir = os.path.join("runs", run_id)
        os.makedirs(os.path.join(run_dir, "diagnostics"), exist_ok=True)

        # 1. Audit Subsystem Preflight
        audit_engine = AuditEngine(run_dir)
        preflight_res = audit_engine.run_preflight_audit({
            "local_model_accessible": True,
            "api_key_present": bool(os.environ.get("GEMINI_API_KEY"))
        })
        console.print(f"[yellow]Preflight Audit Status: {preflight_res.status}[/yellow]")

        # 2. Intelligence Provider & Target Model Setup
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            intelligence = GeminiProvider({"api_key": api_key})
        else:
            intelligence = MockProvider({})

        model = SubprocessCLIAdapter({"command": "python3 -u -m tests.fixtures.dummy_model"})

        # 3. Diagnostic Engine Execution
        engine = AdaptiveDiagnosticEngine(intelligence, model)
        report = await engine.run_diagnostic_run(run_id, max_turns=max_turns)

        # 4. Export Artifacts
        report_path = os.path.join(run_dir, "diagnostics", "diagnostic_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        # 5. Final Audit
        final_res = audit_engine.run_final_audit({"diagnostics_complete": True})
        console.print(f"[bold green]Run '{run_id}' completed successfully! Final Audit: {final_res.status}[/bold green]")
        console.print(f"[blue]Artifacts exported to: {run_dir}/[/blue]")

    asyncio.run(_async_run())

if __name__ == "__main__":
    app()

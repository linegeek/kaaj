"""Hatchet worker entrypoint. Run with: python -m app.workflows.worker"""
from app.engine.rules.registry import RuleEvaluatorRegistry
from app.workflows.underwriting import register_workflow
from app.workflows.hatchet_client import hatchet


def main() -> None:
    RuleEvaluatorRegistry.ensure_loaded()
    register_workflow()
    worker = hatchet.worker("kaaj-worker", max_runs=10)
    worker.start()


if __name__ == "__main__":
    main()

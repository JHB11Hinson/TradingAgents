"""Evaluation harness (D1-REQ-EVAL-001, D1-REQ-COST-001).

``python -m eval.run`` is the entry point; the rules live in
``src/tradingagents/evaluation/`` and the deterministic backend in
``eval/replay.py``. Kept out of the installed package on purpose: this is a
development and CI tool, not part of the shipped application.
"""

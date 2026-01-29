# 12 Business AI Workflow Models
Each folder is a self-contained mini-repo you can drop into GitHub.
They all run the same way: edit `prompt.py`, put input in `examples/input.txt`, run `python main.py`.

## Included models
- **01-lead-triage**: Lead Triage + Prioritization - Score inbound leads, route them to the right pipeline, and generate a next-step plan.
- **02-sales-followup**: Sales Follow-up Writer - Creates short, high-converting follow-ups tailored to the stage and objections.
- **03-support-router**: Support Ticket Router - Classifies support tickets and suggests replies, tags, and escalation paths.
- **04-meeting-actionizer**: Meeting Notes → Action Items - Turns messy notes/transcripts into decisions, owners, due dates, and next steps.
- **05-sop-generator**: SOP + Checklist Generator - Turns a process description into an SOP with steps, QA checks, and a checklist.
- **06-invoice-reconciler**: Invoice + Expense Reconciler - Flags duplicates, mismatches, missing fields, and suggests fixes.
- **07-inventory-reorder**: Inventory Reorder Planner - Suggests reorder points and draft POs based on simple inputs.
- **08-content-calendar**: Content Calendar Builder - Creates a 30-day content plan with hooks, formats, and posting cadence.
- **09-hr-screening**: HR Resume Screener - Screens candidates against a role and writes interview questions.
- **10-compliance-checker**: Policy + Compliance Checker - Checks a draft against policy rules and surfaces risks and edits.
- **11-scope-estimator**: Project Scope + Estimate - Converts a client request into scope, milestones, timeline, and risks.
- **12-kpi-insights**: KPI Insights Writer - Turns metrics dumps into insights, causes, and recommended actions.

## Quick start (any model)
```bash
cd 01-lead-triage
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py --in examples/input.txt --out out.md
```

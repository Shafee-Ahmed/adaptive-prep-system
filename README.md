# Adaptive MCQ Preparation System

Adaptive MCQ Preparation System turns the SLATEFALL dossier into adaptive multiple-choice practice. It extracts section text, generates questions locally, scores attempts, and increases the weight of weak topics over time.

## Why these tools

- FastAPI: compact async API with typed request and response models.
- Ollama: local model execution with no external API key.
- PyMuPDF: stable PDF text extraction for section-based generation.
- SQLite: simple persistence for sessions, attempts, and topic tracking.

## What It Does

- Generates MCQs for selected dossier sections.
- Stores completed sessions and question attempts in SQLite.
- Tracks wrong answers by topic and promotes weak topics after repeated misses.
- Avoids mastered topics when generating later question sets.

## Project Layout

```text
app/
	main.py                 FastAPI entry point
	api/                    Routes, schemas, and dependency wiring
	core/                   Use cases and domain entities
	infrastructure/         SQLite, PDF, and LLM implementations
	utils/                  Configuration, logging, and exceptions
scripts/                  Scenario runners and answer simulation
data/                     Database file and SLATEFALL PDF
docker/                   Dockerfile and compose config
outputs/                  Saved scenario results
```

## Setup

### Local

1. Create and activate a virtual environment.
2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Start Ollama and pull the model.

```bash
ollama serve
ollama pull llama3.2:1b
```

4. Copy `SLATEFALL_DOSSIER.pdf` into `data/`.
5. Copy `.env.example` to `.env` if you want to override defaults.

### Docker

```bash
docker compose -f docker/docker-compose.yml up --build -d
```

The compose file starts the app and a local Ollama service.

## Run the API

```bash
uvicorn app.main:app --reload
```

Useful endpoints:

- `POST /prep/generate` generates MCQs for the requested sections.
- `POST /prep/submit` submits answers and returns scoring with clarifications.
- `POST /kb/snapshot` returns weak-topic and session-history data.
- `GET /health` checks service status.

## Scenario Scripts

- `scripts/run_scenario_a.py` runs a cold-start scenario over two sections (sections 1 and 2) and saves outputs under `outputs/scenario_a/`.
- `scripts/run_scenario_b.py` runs three adaptive iterations and saves outputs under `outputs/scenario_b_iter*/`.
- `scripts/simulate_answers.py` generates answer patterns for testing adaptation.

Example:

```bash
python scripts/run_scenario_b.py
```

## Data Model

SQLite stores three tables:

- `sessions`: session metadata, chosen sections, and final score.
- `question_attempts`: one row per answered question linked back to a session.
- `topic_performance`: wrong-answer counts for each `(section_id, topic)` pair.

The weak-topic threshold is `wrong_count >= 2`.

## Outputs

Generated artifacts are written to:

- `outputs/scenario_b_iter1/`
- `outputs/scenario_b_iter2/`
- `outputs/scenario_b_iter3/`

Each iteration stores a questions JSON file and a knowledge-base snapshot JSON file.

## Configuration

- `LLM_PROVIDER` defaults to `ollama`.
- `OLLAMA_HOST` defaults to `http://localhost:11434`.
- `DATABASE_PATH` defaults to `data/kb.db`.
- `PDF_PATH` defaults to `data/SLATEFALL_DOSSIER.pdf`.
- `LOG_LEVEL` defaults to `INFO`.

## Notes

- No paid API is required.
- The first model pull can take time because the weights are downloaded locally.
- Delete `data/kb.db` if you want to reset the knowledge base.

## Troubleshooting

- If Ollama is not reachable, make sure `ollama serve` is running.
- If the model is missing, run `ollama pull llama3.2:1b`.
- If the PDF is missing, place `SLATEFALL_DOSSIER.pdf` in `data/`.

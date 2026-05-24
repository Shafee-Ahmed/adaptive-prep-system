# Adaptive MCQ Preparation System – SLATEFALL Dossier

A backend system that generates adaptive multiple-choice questions from the **SLATEFALL PAMC dossier**, tracks user performance, and dynamically adjusts future questions based on historical weak areas.
## Tech Stack

- **Backend:** FastAPI  
- **LLM:** Ollama with Llama 3.2 (1B) – fully local, no API key  
- **PDF Parsing:** PyMuPDF  
- **Database:** SQLite  
- **Language:** Python 3.10+  

## Prerequisites

- Python 3.10 or higher  
- Ollama installed – https://ollama.com/download

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Shafee-Ahmed/adaptive-prep-system.git
cd adaptive-prep-system
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Pull the LLM model
```bash
ollama pull llama3.2:1b
```
### 5. Set up environment variables
```bash
cp .env.example .env
```
### 6. Add the PDF dossier
Copy SLATEFALL_DOSSIER.pdf to the data/ folder 

## Run The Project test the scenario for B
```bash
python scripts/run_scenario_b.py
```
## Installation through Docker
#### Start the containers
```bash 
docker-compose -f docker/docker-compose.yml up -d
```
#### (One-time) pull model inside ollama container
```bash 
docker exec -it $(docker ps -q -f name=ollama) ollama pull llama3.2:1b
```
#### Run Scenario B inside app container
```bash 
docker exec -it $(docker ps -q -f name=app) python scripts/run_scenario_b.py
```


### 1. Outputs are saved in:
`outputs/scenario_b_iter1/questions_iter1.json
`
`
 outputs/scenario_b_iter1/kb_snapshot_iter1.json
`
`
 outputs/scenario_b_iter2/questions_iter2.json
`
`
 outputs/scenario_b_iter2/kb_snapshot_iter2.json
`
`
outputs/scenario_b_iter3/questions_iter3.json
`
`
outputs/scenario_b_iter3/kb_snapshot_iter3.json
`


## API Endpoints

### Method Endpoint Description
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /prep/generate | Generate MCQs for given sections |
| POST | /prep/submit | Submit answers and get scoring |
| POST | /kb/snapshot | Get knowledge base snapshot |

## How Adaptation Works
#### 1. User answers questions in a session
#### 2. Wrong answers are tracked by topic
#### 3. Topics with 2+ wrong answers become &quot;weak topics&quot;
#### 4. Next session focuses on weak topics
#### 5. Mastered topics are avoided
## Project Structure
```
adaptive-prep-system/
├── app/
│ ├── api/ # REST endpoints
│ ├── core/ # logic
│ ├── infrastructure/ # DB, PDF, LLM
│ └── utils/ # Config, logging
├── scripts/ # CLI evaluation
├── data/ # PDF and database
└── outputs/ # Generated JSON files
```
## Notes :
 #### No paid APIs required – runs with local Ollama
 #### First run downloads model (~1.5GB)
 #### Outputs saved in required folder structure
 #### To reset knowledge base: delete data/kb.db
## Troubleshooting
 #### Ollama connection error: Run ``` ollama serve ```
 #### Model not found: Run ```ollama pull llama3.2:1b```
 #### PDF not found: Copy dossier to data/ folder

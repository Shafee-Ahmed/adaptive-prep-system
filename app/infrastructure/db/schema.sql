CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    sections TEXT NOT NULL,
    score REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS question_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    topic TEXT,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    clarification TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS topic_performance (
    section_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    wrong_count INTEGER DEFAULT 0,
    last_asked TEXT NOT NULL,
    PRIMARY KEY (section_id, topic)
);
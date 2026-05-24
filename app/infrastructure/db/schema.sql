-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    sections TEXT NOT NULL,  -- JSON array, e.g., "[5,8]"
    score REAL NOT NULL
);

-- Question attempts table
CREATE TABLE IF NOT EXISTS question_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    topic TEXT,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,  -- 1 for true, 0 for false
    clarification TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Topics tracking (for weak topic identification)
CREATE TABLE IF NOT EXISTS topic_performance (
    section_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    wrong_count INTEGER DEFAULT 0,
    last_asked TEXT NOT NULL,
    PRIMARY KEY (section_id, topic)
);
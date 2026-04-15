-- ============================================================
--  Taskboard — Full SQL Schema
--  Compatible with: PostgreSQL 14+ / MySQL 8+ / SQLite 3.35+
-- ============================================================

-- ── TASKS ────────────────────────────────────────────────────
CREATE TABLE tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- use TEXT for SQLite
    topic       VARCHAR(255)  NOT NULL,
    subtopic    VARCHAR(255),
    description TEXT,
    due_date    DATE,
    completed   BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ── SUBTASKS ─────────────────────────────────────────────────
CREATE TABLE subtasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id     UUID          NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title       VARCHAR(255)  NOT NULL,
    description TEXT,
    -- due_date must be <= parent task due_date (enforced by CHECK constraint below)
    due_date    DATE,
    completed   BOOLEAN       NOT NULL DEFAULT FALSE,
    sort_order  INT           NOT NULL DEFAULT 0,  -- for manual ordering
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW(),

    -- Ensure subtask due date does not exceed task due date
    CONSTRAINT subtask_due_within_task
        CHECK (
            due_date IS NULL OR
            (SELECT due_date FROM tasks WHERE id = task_id) IS NULL OR
            due_date <= (SELECT due_date FROM tasks WHERE id = task_id)
        )
);

-- ── CHECKLIST ITEMS (per subtask) ───────────────────────────
CREATE TABLE checklist_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subtask_id  UUID          NOT NULL REFERENCES subtasks(id) ON DELETE CASCADE,
    text        VARCHAR(500)  NOT NULL,
    checked     BOOLEAN       NOT NULL DEFAULT FALSE,
    sort_order  INT           NOT NULL DEFAULT 0,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ── COMMENTS (on tasks) ─────────────────────────────────────
CREATE TABLE comments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id     UUID          NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    text        TEXT          NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ── INDEXES ─────────────────────────────────────────────────
CREATE INDEX idx_subtasks_task_id       ON subtasks(task_id);
CREATE INDEX idx_checklist_subtask_id   ON checklist_items(subtask_id);
CREATE INDEX idx_comments_task_id       ON comments(task_id);
CREATE INDEX idx_tasks_due_date         ON tasks(due_date);
CREATE INDEX idx_tasks_completed        ON tasks(completed);
CREATE INDEX idx_subtasks_completed     ON subtasks(completed);

-- ============================================================
--  USEFUL QUERIES
-- ============================================================

-- 1. All tasks with subtask progress
SELECT
    t.id,
    t.topic,
    t.subtopic,
    t.due_date,
    t.completed,
    COUNT(s.id)                                          AS total_subtasks,
    SUM(CASE WHEN s.completed THEN 1 ELSE 0 END)        AS done_subtasks,
    ROUND(
        100.0 * SUM(CASE WHEN s.completed THEN 1 ELSE 0 END)
              / NULLIF(COUNT(s.id), 0), 1
    )                                                    AS pct_complete
FROM tasks t
LEFT JOIN subtasks s ON s.task_id = t.id
GROUP BY t.id
ORDER BY t.created_at DESC;

-- 2. Auto-complete a task when all its subtasks are done
--    (Run this after toggling a subtask, or as a trigger)
UPDATE tasks t
SET completed = TRUE
WHERE t.id = :task_id
  AND NOT EXISTS (
      SELECT 1 FROM subtasks s
      WHERE s.task_id = t.id
        AND s.completed = FALSE
  )
  AND EXISTS (
      SELECT 1 FROM subtasks s WHERE s.task_id = t.id
  );

-- 3. Checklist progress per subtask
SELECT
    s.id            AS subtask_id,
    s.title,
    COUNT(c.id)     AS total_items,
    SUM(CASE WHEN c.checked THEN 1 ELSE 0 END) AS checked_items
FROM subtasks s
LEFT JOIN checklist_items c ON c.subtask_id = s.id
GROUP BY s.id, s.title;

-- 4. Overdue tasks (not completed, past due date)
SELECT * FROM tasks
WHERE completed = FALSE
  AND due_date < CURRENT_DATE
ORDER BY due_date ASC;

-- 5. Overdue subtasks
SELECT
    t.topic AS task_name,
    s.*
FROM subtasks s
JOIN tasks t ON t.id = s.task_id
WHERE s.completed = FALSE
  AND s.due_date < CURRENT_DATE
ORDER BY s.due_date ASC;

-- ============================================================
--  TRIGGER: Auto-complete task when all subtasks done
--  (PostgreSQL syntax)
-- ============================================================

CREATE OR REPLACE FUNCTION auto_complete_task()
RETURNS TRIGGER AS $$
BEGIN
    -- When a subtask is updated to completed, check if all are done
    IF NEW.completed = TRUE THEN
        UPDATE tasks
        SET completed = TRUE
        WHERE id = NEW.task_id
          AND NOT EXISTS (
              SELECT 1 FROM subtasks
              WHERE task_id = NEW.task_id
                AND completed = FALSE
                AND id != NEW.id
          );
    ELSE
        -- If a subtask is unchecked, un-complete the parent task
        UPDATE tasks
        SET completed = FALSE
        WHERE id = NEW.task_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_subtask_auto_complete
AFTER UPDATE OF completed ON subtasks
FOR EACH ROW
EXECUTE FUNCTION auto_complete_task();

-- ============================================================
--  SQLITE-COMPATIBLE VERSION (use TEXT for UUIDs, no CHECK
--  subquery, no stored trigger syntax)
-- ============================================================
/*
CREATE TABLE tasks (
    id          TEXT PRIMARY KEY,
    topic       TEXT NOT NULL,
    subtopic    TEXT,
    description TEXT,
    due_date    TEXT,  -- stored as YYYY-MM-DD
    completed   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE subtasks (
    id          TEXT PRIMARY KEY,
    task_id     TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    due_date    TEXT,
    completed   INTEGER NOT NULL DEFAULT 0,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE checklist_items (
    id          TEXT PRIMARY KEY,
    subtask_id  TEXT NOT NULL REFERENCES subtasks(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    checked     INTEGER NOT NULL DEFAULT 0,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE comments (
    id          TEXT PRIMARY KEY,
    task_id     TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
*/

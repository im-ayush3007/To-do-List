# Taskboard — Flask To-Do App

A clean, dark-themed to-do list app built with Flask.

## Features
- Add tasks with Topic, Sub-topic, Description, and Due Date
- Check/uncheck tasks as complete
- Edit any task in a modal
- Delete tasks
- Add and delete comments per task
- Filter by All / Pending / Completed / Overdue
- Due date color coding (overdue = red, today = gold, soon = green)
- Data persisted in `todos.json`

## Setup

```bash
cd todo_app
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

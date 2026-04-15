from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os, uuid
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'todos.json'

def load_todos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(DATA_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

@app.route('/')
def index():
    todos = load_todos()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    todos = load_todos()
    todo = {
        'id': str(uuid.uuid4()),
        'topic': request.form.get('topic', '').strip(),
        'subtopic': request.form.get('subtopic', '').strip(),
        'description': request.form.get('description', '').strip(),
        'due_date': request.form.get('due_date', ''),
        'completed': False,
        'comments': [],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    todos.append(todo)
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/toggle/<id>', methods=['POST'])
def toggle(id):
    todos = load_todos()
    for t in todos:
        if t['id'] == id:
            t['completed'] = not t['completed']
            break
    save_todos(todos)
    return jsonify({'success': True})

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    todos = load_todos()
    todos = [t for t in todos if t['id'] != id]
    save_todos(todos)
    return jsonify({'success': True})

@app.route('/edit/<id>', methods=['POST'])
def edit(id):
    todos = load_todos()
    for t in todos:
        if t['id'] == id:
            t['topic'] = request.form.get('topic', '').strip()
            t['subtopic'] = request.form.get('subtopic', '').strip()
            t['description'] = request.form.get('description', '').strip()
            t['due_date'] = request.form.get('due_date', '')
            break
    save_todos(todos)
    return redirect(url_for('index'))

@app.route('/comment/<id>', methods=['POST'])
def add_comment(id):
    todos = load_todos()
    text = request.form.get('comment', '').strip()
    if text:
        for t in todos:
            if t['id'] == id:
                t['comments'].append({
                    'id': str(uuid.uuid4()),
                    'text': text,
                    'created_at': datetime.now().strftime('%b %d, %H:%M')
                })
                break
        save_todos(todos)
    return jsonify({'success': True, 'comment': text})

@app.route('/comment/delete/<todo_id>/<comment_id>', methods=['POST'])
def delete_comment(todo_id, comment_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            t['comments'] = [c for c in t['comments'] if c['id'] != comment_id]
            break
    save_todos(todos)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)

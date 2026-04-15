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

def auto_complete_task(task):
    subtasks = task.get('subtasks', [])
    if subtasks and all(st.get('completed', False) for st in subtasks):
        task['completed'] = True
    elif subtasks and not all(st.get('completed', False) for st in subtasks):
        task['completed'] = False

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
        'subtasks': [],
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

# SUBTASK ROUTES
@app.route('/subtask/add/<todo_id>', methods=['POST'])
def add_subtask(todo_id):
    todos = load_todos()
    data = request.get_json()
    for t in todos:
        if t['id'] == todo_id:
            subtask = {
                'id': str(uuid.uuid4()),
                'title': data.get('title', '').strip(),
                'description': data.get('description', '').strip(),
                'due_date': data.get('due_date', ''),
                'completed': False,
                'checklist': [],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            if 'subtasks' not in t:
                t['subtasks'] = []
            t['subtasks'].append(subtask)
            auto_complete_task(t)
            save_todos(todos)
            return jsonify({'success': True, 'subtask': subtask})
    return jsonify({'success': False}), 404

@app.route('/subtask/toggle/<todo_id>/<subtask_id>', methods=['POST'])
def toggle_subtask(todo_id, subtask_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            for st in t.get('subtasks', []):
                if st['id'] == subtask_id:
                    st['completed'] = not st['completed']
                    break
            auto_complete_task(t)
            save_todos(todos)
            return jsonify({'success': True, 'task_completed': t['completed']})
    return jsonify({'success': False}), 404

@app.route('/subtask/delete/<todo_id>/<subtask_id>', methods=['POST'])
def delete_subtask(todo_id, subtask_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            t['subtasks'] = [st for st in t.get('subtasks', []) if st['id'] != subtask_id]
            auto_complete_task(t)
            save_todos(todos)
            return jsonify({'success': True, 'task_completed': t['completed']})
    return jsonify({'success': False}), 404

@app.route('/subtask/edit/<todo_id>/<subtask_id>', methods=['POST'])
def edit_subtask(todo_id, subtask_id):
    todos = load_todos()
    data = request.get_json()
    for t in todos:
        if t['id'] == todo_id:
            for st in t.get('subtasks', []):
                if st['id'] == subtask_id:
                    st['title'] = data.get('title', st['title']).strip()
                    st['description'] = data.get('description', st['description']).strip()
                    st['due_date'] = data.get('due_date', st['due_date'])
                    break
            save_todos(todos)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

# CHECKLIST ROUTES
@app.route('/checklist/add/<todo_id>/<subtask_id>', methods=['POST'])
def add_checklist_item(todo_id, subtask_id):
    todos = load_todos()
    data = request.get_json()
    for t in todos:
        if t['id'] == todo_id:
            for st in t.get('subtasks', []):
                if st['id'] == subtask_id:
                    item = {
                        'id': str(uuid.uuid4()),
                        'text': data.get('text', '').strip(),
                        'checked': False
                    }
                    if 'checklist' not in st:
                        st['checklist'] = []
                    st['checklist'].append(item)
                    save_todos(todos)
                    return jsonify({'success': True, 'item': item})
    return jsonify({'success': False}), 404

@app.route('/checklist/toggle/<todo_id>/<subtask_id>/<item_id>', methods=['POST'])
def toggle_checklist_item(todo_id, subtask_id, item_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            for st in t.get('subtasks', []):
                if st['id'] == subtask_id:
                    for item in st.get('checklist', []):
                        if item['id'] == item_id:
                            item['checked'] = not item['checked']
                            break
                    save_todos(todos)
                    checklist = st.get('checklist', [])
                    checked_count = sum(1 for i in checklist if i.get('checked'))
                    return jsonify({'success': True, 'checked': checked_count, 'total': len(checklist)})
    return jsonify({'success': False}), 404

@app.route('/checklist/delete/<todo_id>/<subtask_id>/<item_id>', methods=['POST'])
def delete_checklist_item(todo_id, subtask_id, item_id):
    todos = load_todos()
    for t in todos:
        if t['id'] == todo_id:
            for st in t.get('subtasks', []):
                if st['id'] == subtask_id:
                    st['checklist'] = [i for i in st.get('checklist', []) if i['id'] != item_id]
                    save_todos(todos)
                    return jsonify({'success': True})
    return jsonify({'success': False}), 404

if __name__ == '__main__':
    app.run(debug=True)

from flask import render_template, request, redirect, url_for, jsonify, current_app
from app import app, db
from models import Todo, Subtask
import uuid
from datetime import datetime

@app.route('/')
def index():
    current_app.logger.info("Loading index page")
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    try:
        todo = Todo(
            id=str(uuid.uuid4()),
            topic=request.form.get('topic'),
            subtopic=request.form.get('subtopic'),
            description=request.form.get('description'),
            due_date=request.form.get('due_date'),
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M')
        )

        db.session.add(todo)
        db.session.commit()

        current_app.logger.info(f"Task created: {todo.id}")
        return redirect(url_for('index'))

    except Exception as e:
        current_app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    try:
        todo = Todo.query.get(id)
        db.session.delete(todo)
        db.session.commit()

        current_app.logger.info(f"Task deleted: {id}")
        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Error deleting task {id}: {str(e)}")
        return jsonify({'error': 'Delete failed'}), 500

@app.route('/toggle/<id>', methods=['POST'])
def toggle(id):
    try:
        todo = Todo.query.get(id)
        todo.completed = not todo.completed
        db.session.commit()

        current_app.logger.info(f"Task toggled: {id} -> {todo.completed}")
        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Toggle error {id}: {str(e)}")
        return jsonify({'error': 'Toggle failed'}), 500

@app.route('/subtask/add/<todo_id>', methods=['POST'])
def add_subtask(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json() or {}
        subtask = Subtask(
            id=str(uuid.uuid4()),
            todo_id=todo_id,
            title=data.get('title'),
            description=data.get('description'),
            due_date=data.get('due_date'),
            completed=False
        )

        db.session.add(subtask)
        db.session.commit()

        current_app.logger.info(f"Subtask created: {subtask.id} for task {todo_id}")
        return jsonify({
            'success': True,
            'subtask': {
                'id': subtask.id,
                'title': subtask.title,
                'description': subtask.description or '',
                'due_date': subtask.due_date or '',
                'completed': subtask.completed
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error creating subtask for {todo_id}: {str(e)}")
        return jsonify({'error': 'Failed to create subtask'}), 500

@app.route('/subtask/toggle/<todo_id>/<subtask_id>', methods=['POST'])
def toggle_subtask(todo_id, subtask_id):
    try:
        subtask = Subtask.query.get(subtask_id)
        if not subtask or subtask.todo_id != todo_id:
            return jsonify({'error': 'Subtask not found'}), 404

        subtask.completed = not subtask.completed
        db.session.commit()

        current_app.logger.info(f"Subtask toggled: {subtask.id} -> {subtask.completed}")
        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Toggle subtask error {subtask_id}: {str(e)}")
        return jsonify({'error': 'Toggle failed'}), 500

@app.route('/subtask/delete/<todo_id>/<subtask_id>', methods=['POST'])
def delete_subtask(todo_id, subtask_id):
    try:
        subtask = Subtask.query.get(subtask_id)
        if not subtask or subtask.todo_id != todo_id:
            return jsonify({'error': 'Subtask not found'}), 404

        db.session.delete(subtask)
        db.session.commit()

        current_app.logger.info(f"Subtask deleted: {subtask_id}")
        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Delete subtask error {subtask_id}: {str(e)}")
        return jsonify({'error': 'Delete failed'}), 500

@app.route('/subtask/edit/<todo_id>/<subtask_id>', methods=['POST'])
def edit_subtask(todo_id, subtask_id):
    try:
        subtask = Subtask.query.get(subtask_id)
        if not subtask or subtask.todo_id != todo_id:
            return jsonify({'error': 'Subtask not found'}), 404

        data = request.get_json() or {}
        subtask.title = data.get('title', subtask.title)
        subtask.description = data.get('description', subtask.description)
        subtask.due_date = data.get('due_date', subtask.due_date)

        db.session.commit()

        current_app.logger.info(f"Subtask updated: {subtask.id}")
        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Edit subtask error {subtask_id}: {str(e)}")
        return jsonify({'error': 'Edit failed'}), 500
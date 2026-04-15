from app import db

class Todo(db.Model):
    id = db.Column(db.String, primary_key=True)
    topic = db.Column(db.String(200))
    subtopic = db.Column(db.String(200))
    description = db.Column(db.Text)
    due_date = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.String(50))

    comments = db.relationship(
        'Comment',
        backref='todo',
        cascade='all, delete-orphan',
        lazy='select'
    )
    subtasks = db.relationship(
        'Subtask',
        backref='todo',
        cascade='all, delete-orphan',
        lazy='select'
    )


class Comment(db.Model):
    id = db.Column(db.String, primary_key=True)
    todo_id = db.Column(db.String, db.ForeignKey('todo.id'))
    text = db.Column(db.Text)
    created_at = db.Column(db.String(50))


class Subtask(db.Model):
    id = db.Column(db.String, primary_key=True)
    todo_id = db.Column(db.String, db.ForeignKey('todo.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    due_date = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)

    @property
    def checklist(self):
        return []
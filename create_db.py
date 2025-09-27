from project.app import app, db
from project.models import Post  # ensure model is registered with metadata

with app.app_context():
    db.create_all()
    db.session.commit()
    print("Database tables created.")

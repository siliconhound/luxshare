from app import create_app

app = create_app()

from app import cli, db

cli.register(app)


@app.shell_context_processor
def make_shell_context():
  return {
      "db": db
  }

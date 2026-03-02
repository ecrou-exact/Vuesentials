from app import create_app
from flask import render_template, request, Response
import json
import os




os.environ.setdefault('FLASKENV', 'development')

app = create_app()

@app.errorhandler(404)
def error_page_not_found(e):
    if request.path.startswith('/api/'):
        return Response(json.dumps({"status": "error", "reason": "404 Not Found"}, indent=2, sort_keys=True), mimetype='application/json'), 404
    return render_template('404.html'), 404
    


app.run(host=app.config.get("FLASK_URL"), port=app.config.get("FLASK_PORT"))
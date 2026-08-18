"""Flask sample for Portainer-Run release testing.

Unlike python-hello, this one has a requirements.txt, so it exercises the
Python install init container:

    pip install --no-cache-dir --target=/app/.pydeps -r requirements.txt

pip's default target is the image's system site-packages, which sit outside
the shared PersistentVolume and would be lost when the init container exits.
The install goes to /app/.pydeps instead, and the app container picks it up
via PYTHONPATH. If `import flask` fails at startup, that wiring is what
broke — python-hello will still be green, which is how you tell the two
apart.

Run directly with `python app.py` (the detected start command), not through
gunicorn, so the port must be bound here. The expected port is 8000.
"""

import importlib.metadata
import os
import platform
import socket

import flask

PORT = int(os.environ.get("PORT", 8000))
GREETING = os.environ.get("GREETING", "Flask is running.")

app = flask.Flask(__name__)


@app.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/")
def index():
    return flask.render_template_string(
        """<!doctype html>
<meta charset="utf-8">
<title>python-flask</title>
<style>
  body { font: 16px/1.6 system-ui, sans-serif; max-width: 40rem; margin: 4rem auto; padding: 0 1rem; }
  h1 { font-size: 1.4rem; }
  .ok { color: #137333; font-weight: 600; }
  code { background: #f4f4f4; padding: .1rem .3rem; border-radius: 3px; }
</style>
<h1>python-flask</h1>
<p class="ok">{{ greeting }}</p>
<p>Flask imported successfully, so <code>pip install --target</code> and
<code>PYTHONPATH</code> are both wired up correctly.</p>
<ul>
  <li>Flask version: {{ flask_version }}</li>
  <li>Python version: {{ python_version }}</li>
  <li>Hostname: {{ hostname }}</li>
  <li>Listening port: {{ port }}</li>
  <li>Package path: <code>{{ flask_path }}</code></li>
</ul>
""",
        greeting=GREETING,
        # Not flask.__version__ — deprecated in 3.1 and it logs a warning that
        # reads like a real problem in the Logs tab.
        flask_version=importlib.metadata.version("flask"),
        python_version=platform.python_version(),
        hostname=socket.gethostname(),
        port=PORT,
        flask_path=os.path.dirname(flask.__file__),
    )


if __name__ == "__main__":
    print(f"python-flask listening on 0.0.0.0:{PORT}", flush=True)
    app.run(host="0.0.0.0", port=PORT)

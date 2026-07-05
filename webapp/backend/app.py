"""
app.py — Flask REST API for FIFA World Cup 2026 Predictor
"""

import os
import threading
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from webapp.backend.simulation import (
    get_teams_data,
    get_groups_data,
    load_results,
    load_bracket,
    run_random_simulation,
    run_scheduled_simulation,
)

app = Flask(__name__)
CORS(app, origins="*")

# In-memory job store  {job_id: {status, progress, result, error}}
_jobs = {}
_jobs_lock = threading.Lock()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get('/api/status')
def status():
    return jsonify({'status': 'ok', 'message': 'FIFA WC 2026 Predictor API running'})


# ─── Teams & Groups ───────────────────────────────────────────────────────────

@app.get('/api/teams')
def teams():
    try:
        data = get_teams_data()
        return jsonify({'teams': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.get('/api/groups')
def groups():
    try:
        data = get_groups_data()
        return jsonify({'groups': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Cached Results ───────────────────────────────────────────────────────────

@app.get('/api/results/random')
def results_random():
    try:
        data = load_results('random')
        return jsonify({'results': data, 'mode': 'random'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.get('/api/results/scheduled')
def results_scheduled():
    try:
        data = load_results('scheduled')
        return jsonify({'results': data, 'mode': 'scheduled'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.get('/api/bracket/<mode>')
def bracket(mode):
    try:
        data = load_bracket('scheduled' if mode == 'scheduled' else 'random')
        return jsonify({'bracket': data, 'mode': mode})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Simulation Job ───────────────────────────────────────────────────────────

def _run_sim_job(job_id, mode, num_simulations):
    def on_progress(pct):
        with _jobs_lock:
            if job_id in _jobs:
                _jobs[job_id]['progress'] = pct

    try:
        with _jobs_lock:
            _jobs[job_id]['status'] = 'running'

        if mode == 'scheduled':
            df = run_scheduled_simulation(num_simulations, progress_cb=on_progress)
        else:
            df = run_random_simulation(num_simulations, progress_cb=on_progress)

        results = load_results(mode)
        with _jobs_lock:
            _jobs[job_id]['status'] = 'done'
            _jobs[job_id]['progress'] = 100
            _jobs[job_id]['result'] = results

    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]['status'] = 'error'
            _jobs[job_id]['error'] = str(e)


@app.post('/api/simulate')
def simulate():
    body = request.get_json(silent=True) or {}
    mode = body.get('mode', 'random')
    try:
        num_simulations = int(body.get('num_simulations', 1000))
        num_simulations = max(100, min(20000, num_simulations))
    except (TypeError, ValueError):
        num_simulations = 1000

    job_id = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _jobs[job_id] = {'status': 'queued', 'progress': 0, 'result': None, 'error': None}

    thread = threading.Thread(target=_run_sim_job, args=(job_id, mode, num_simulations), daemon=True)
    thread.start()

    return jsonify({'job_id': job_id, 'status': 'queued'}), 202


@app.get('/api/simulate/status/<job_id>')
def simulate_status(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'result': job['result'] if job['status'] == 'done' else None,
        'error': job['error'],
    })


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)), threaded=True)
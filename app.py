from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os, json, zipfile

app = Flask(__name__)
BASE_DIR = "data"
os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    pid = request.form.get('participant_id')
    name = request.form.get('participant_name')
    test_time = request.form.get('test_time')
    consent = request.form.get('consent')
    consent_ts = request.form.get('consent_timestamp')
    zip_file = request.files.get('zipfile')

    if not all([pid, name, test_time, consent, consent_ts, zip_file]):
        return jsonify({'error': 'Missing fields'}), 400

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    subject_dir = os.path.join(BASE_DIR, f"{pid}_{timestamp}")
    os.makedirs(subject_dir, exist_ok=True)

    zip_path = os.path.join(subject_dir, 'recordings.zip')
    zip_file.save(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(os.path.join(subject_dir, 'recordings'))

    metadata = {
        'participant_id': pid,
        'participant_name': name,
        'test_time': test_time,
        'consent': consent == 'true',
        'consent_timestamp': consent_ts,
        'submission_time': datetime.now().isoformat(),
        'n_recordings': len(os.listdir(os.path.join(subject_dir, 'recordings')))
    }

    with open(os.path.join(subject_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
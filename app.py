import os
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Absolute paths within the Docker container
INPUT_FOLDER = os.environ.get('INPUT_FOLDER', '/app/input')
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', '/app/output')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    try:
        files = []
        if os.path.exists(INPUT_FOLDER):
            for f in os.listdir(INPUT_FOLDER):
                if os.path.isfile(os.path.join(INPUT_FOLDER, f)):
                    files.append(f)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/encode', methods=['POST'])
def encode_video():
    data = request.json
    filename = data.get('filename')
    codec = data.get('codec', 'libx264')
    crf = data.get('crf', '23')
    preset = data.get('preset', 'medium')
    
    if not filename:
        return jsonify({'error': 'No file selected'}), 400

    input_path = os.path.join(INPUT_FOLDER, filename)
    
    if not os.path.exists(input_path):
        return jsonify({'error': f'File not found: {filename}'}), 404

    # Generate output filename
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_encoded{ext}"
    if codec in ['libvpx-vp9', 'libaom-av1']:
        output_filename = f"{name}_encoded.mkv"
    elif codec == 'libx265':
        output_filename = f"{name}_encoded.mp4"
        
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Basic ffmpeg command
    command = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', codec,
        '-crf', str(crf),
        '-preset', preset,
        '-y', # Overwrite output files without asking
        output_path
    ]

    try:
        # Run ffmpeg asynchronously
        subprocess.Popen(command)
        
        return jsonify({
            'message': 'Encoding started successfully (running in background)',
            'output_file': output_filename,
            'command': ' '.join(command)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, request, send_file
from palette import extract_palette
import os
import json
import time
import zipfile
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def cleanup_old_files(folder, age_seconds=600):
    """Delete files older than age_seconds (default 10 min)"""
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path) and now - os.path.getmtime(path) > age_seconds:
            os.remove(path)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cleanup_old_files(app.config['UPLOAD_FOLDER'])

        image = request.files['image']
        num_colors = int(request.form.get('num_colors', 5))

        if image:
            unique_id = uuid.uuid4().hex
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
            image.save(filepath)

            # Extract color palette
            palette_img_path, hex_colors = extract_palette(filepath, num_colors)

            # Save JSON
            json_path = os.path.splitext(palette_img_path)[0] + '.json'
            with open(json_path, 'w') as f:
                json.dump({"colors": hex_colors}, f)

            # Create ZIP
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_palette.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(palette_img_path, os.path.basename(palette_img_path))
                zipf.write(json_path, os.path.basename(json_path))

            return render_template('index.html',
                                   palette_image=palette_img_path,
                                   hex_colors=hex_colors,
                                   uploaded_image=filepath,
                                   zip_path=zip_path)

    return render_template('index.html')


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

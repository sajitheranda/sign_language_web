import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import cv2
import tempfile
import shutil
from werkzeug.utils import secure_filename
from keypoint_model_load import wholebody
from config import Config
import json
from flask import send_file
from operations import flattern
from pyngrok import ngrok
from result_gen import send_classification , send_translation
import torch


app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_frames(video_path, output_folder, fps=5):
    cap = cv2.VideoCapture(video_path)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(round(original_fps / fps))
    frame_count = 0
    extracted_frames = []
    count = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_folder, f'{str(count).zfill(3)}.jpg')
            cv2.imwrite(frame_path, frame)
            extracted_frames.append(frame_path)
            count += 1
        frame_count += 1

    cap.release()
    return extracted_frames

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No video file selected')
            return redirect(request.url)

        file = request.files['video']
        operation_type = request.form['operation_type']
        print("*** ",operation_type)
        if file.filename == '':
            flash('No video selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            temp_dir = tempfile.mkdtemp(dir=app.config['TEMP_FOLDER'])
            temp_subfolder = os.path.basename(temp_dir)
            filename = secure_filename(file.filename)
            video_path = os.path.join(temp_dir, filename)
            video_url = url_for('static', filename=f'temp/{temp_subfolder}/{filename}')
            file.save(video_path)

            

            # Process immediately after upload
            processing_data = {
                'temp_dir': temp_dir,
                'video_url': video_url,
                'video_name': filename,
                'operation_type' : operation_type
            }
            
            # Step 1: Extract frames
            frames = extract_frames(video_path, temp_dir, fps=5)
            processing_data['frames'] = frames
            
            # Step 2: Extract keypoints
            video_keypoints = []
            images = sorted([img for img in os.listdir(temp_dir) if img.endswith(".jpg")])
            for i, image in enumerate(images):
                frame_id = int(image.split('.')[0].lstrip('0'))
                assert i + 1 == frame_id, f"Frame index mismatch at {image}"

                image_path = os.path.join(temp_dir, image)
                img = cv2.imread(image_path)
                keypoints, scores = wholebody(img)
                keypoints=keypoints[0]
                video_keypoints.append(keypoints.tolist())

            video_keypoints=flattern(video_keypoints)
            print(len(video_keypoints))
            # Save keypoints
            # keypoint_path = os.path.join(temp_dir, 'keypoints.json')

            keypoint_path = os.path.join(temp_dir, 'keypoints.pt')

            # Save the tensor
            torch.save(video_keypoints, keypoint_path)
            # with open(keypoint_path, 'w') as f:
            #     json.dump(video_keypoints, f)
            print("tensor save successful")
            # torch.save(video_keypoints, 'filtered_keypoints.pt')

            video_keypoints = video_keypoints.tolist()[:40]
            
            result_data=""
            
            if operation_type == "classification":
                result_data =send_classification(video_keypoints)
            else:
                result_data=send_translation(video_keypoints)

            print(result_data)

            processing_data['keypoint_path'] = keypoint_path
            processing_data['result_data'] = result_data
            session['processing_data'] = processing_data
            
            return jsonify({
                'status': 'complete',
                'video_name': filename,
                'frame_count': len(frames),
                'operation_type' : operation_type,
                'result_data' : result_data,
                'video_url': video_url,
            })

    # For GET requests or if processing is complete
    if 'processing_data' in session:
        processing_data = session['processing_data']
        return render_template('index.html', 
                             processing_complete=True,
                             video_url =processing_data['video_url'],
                             result_data = processing_data['result_data'],
                             operation_type=processing_data['operation_type'],
                             video_name=processing_data['video_name'],
                             frame_count=len(processing_data['frames']))
    
    return render_template('index.html', processing_complete=False , result_data="")

# @app.route('/processing')
# def processing():
#     if 'processing_data' not in session:
#         return redirect(url_for('index'))

#     processing_data = session['processing_data']
#     video_path = processing_data['video_path']
#     temp_dir = processing_data['temp_dir']

#     # Step 1: Extract frames
#     frames = extract_frames(video_path, temp_dir, fps=5)
#     processing_data['frames'] = frames  # Add frames
#     session['processing_data'] = processing_data  # ✅ Reassign session key

#     # Step 2: Extract keypoints
#     video_keypoints = []
#     images = sorted([img for img in os.listdir(temp_dir) if img.endswith(".jpg")])
#     for i, image in enumerate(images):
#         frame_id = int(image.split('.')[0].lstrip('0'))
#         assert i + 1 == frame_id, f"Frame index mismatch at {image}"

#         image_path = os.path.join(temp_dir, image)
#         img = cv2.imread(image_path)
#         keypoints, scores = wholebody(img)
#         video_keypoints.append(keypoints.tolist())

#     # Save keypoints
#     keypoint_path = os.path.join(temp_dir, 'keypoints.json')
#     with open(keypoint_path, 'w') as f:
#         json.dump(video_keypoints, f)

#     processing_data['keypoint_path'] = keypoint_path  # Add path
#     session['processing_data'] = processing_data  # ✅ Reassign again

#     return render_template('processing.html',
#                            video_name=processing_data['video_name'],
#                            frame_count=len(frames),
#                            keypoint_done=True)

@app.route('/get_keypoints_json')
def get_keypoints_json():
    if 'processing_data' not in session:
        return redirect(url_for('index'))

    keypoint_path = session['processing_data'].get('keypoint_path')
    if not keypoint_path or not os.path.exists(keypoint_path):
        return "Keypoints not found.", 404

    return send_file(keypoint_path, mimetype='application/json', as_attachment=True)

@app.route('/results')
def results():
    if 'processing_data' not in session:
        return redirect(url_for('index'))

    processing_data = session['processing_data']
    frames = [f.replace(app.config['TEMP_FOLDER'], '') for f in processing_data['frames']]

    return render_template('results.html',
                           frames=frames,
                           video_name=processing_data['video_name'])

@app.route('/cleanup', methods=['POST'])
def cleanup():
    if 'processing_data' in session:
        temp_dir = session['processing_data']['temp_dir']
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        session.pop('processing_data', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    # Set your ngrok auth token (only needs to be done once per runtime)
    # ngrok.set_auth_token("2xRoQceut1EqOlv0mRHDz6gwRtp_66KghwXkAuYmWjSXQNshN")  # Replace with your token

    # # Open ngrok tunnel
    # public_url = ngrok.connect(5000)
    # print(f"🌐 Public URL: {public_url}")

    # # Start Flask app
    # app.run(port=5000, debug=True)

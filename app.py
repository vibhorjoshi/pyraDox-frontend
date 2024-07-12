from flask import Flask, request, Response
import jsonpickle
import cv2
import numpy as np
import base64
import os
from Aadhaar import Aadhaar_Card
from PanCard import PanCard

app = Flask(__name__)

config = {
    'orient': True,
    'skew': False,
    'crop': True,
    'contrast': True,
    'psm': [3, 4, 6],
    'mask_color': (0, 165, 255),
    'brut_psm': [6]
}

ac = Aadhaar_Card(config)
pc = PanCard(config)

def to_image_string(image_filepath):
    return base64.b64encode(open(image_filepath, 'rb').read())

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

@app.route('/api/validate', methods=['GET','POST'])
def validate():
    r = request.get_json(force=True)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    if 'aadhaar' in r['type']:
        validity = ac.validate(str(r['test_number']))
    elif 'pan' in r['type']:
        validity = pc.validate(str(r['test_number']))
    else:
        validity = False

    return Response(response=jsonpickle.encode({'validity': validity}), status=200, mimetype="application/json", headers=headers)

@app.route('/api/ocr', methods=['GET','POST'])
def ocr():
    r = request.get_json(force=True)
    temp_name = "123.png"
    image = r['doc_b64']
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name, img)
    content_type = 'application/json'
    headers = {'content-type': content_type}

    if 'aadhaar' in r['type']:
        result_list = ac.extract(temp_name)
    elif 'pan' in r['type']:
        result_list = pc.extract(temp_name)
    else:
        result_list = []

    return Response(response=jsonpickle.encode({'result_list': result_list}), status=200, mimetype="application/json", headers=headers)

@app.route('/api/mask', methods=['GET','POST'])
def mask():
    flag_mask = 0
    r = request.get_json(force=True)
    temp_name = "temp_unmasked.png"
    image = r['doc_b64']
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name, img)
    write = "temp_masked.png"
    
    if 'aadhaar' in r['type']:
        flag_mask = ac.mask_image(temp_name, write, r['aadhaar'])
    elif 'pan' in r['type']:
        flag_mask = pc.mask_image(temp_name, write, r['pan'])
    else:
        flag_mask = 0

    if flag_mask > 0:
        with open(write, 'rb') as f:
            masked_image = f.read()
            masked_image_b64 = base64.b64encode(masked_image).decode('utf-8')
        delete_file(temp_name)
        delete_file(write)
        return Response(response=jsonpickle.encode({'masked_image_b64': masked_image_b64}), status=200, mimetype="application/json")
    else:
        delete_file(temp_name)
        delete_file(write)
        return Response(response=jsonpickle.encode({'masked_image_b64': None}), status=404, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)


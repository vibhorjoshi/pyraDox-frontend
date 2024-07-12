import numpy as np
import cv2
import base64
import requests
import json

def to_image_string(image_filepath):
    return base64.b64encode(open(image_filepath, 'rb').read()).decode('utf-8')

def hit_api_validate(card_type, number):
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:8001'
    if card_type == 'aadhaar':
        url = addr + '/api/validate'
    elif card_type == 'pan':
        url = addr + '/api/validate_pan'
    response = requests.post(url, json={"test_number": number}, headers=headers)
    return json.loads(response.text)

def hit_api_extract(card_type, filepath):
    img_bytes = to_image_string(filepath)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:8001'
    if card_type == 'aadhaar':
        url = addr + '/api/ocr'
    elif card_type == 'pan':
        url = addr + '/api/ocr_pan'
    response = requests.post(url, json={"doc_b64": img_bytes}, headers=headers)
    return json.loads(response.text)

def hit_api_mask(card_type, filepath, number_list):
    img_bytes = to_image_string(filepath)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:8001'
    if card_type == 'aadhaar':
        url = addr + '/api/mask'
    elif card_type == 'pan':
        url = addr + '/api/mask_pan'
    response = requests.post(url, json={"doc_b64": img_bytes, 'number_list': number_list}, headers=headers)
    
    r = json.loads(response.text)
    if r['is_masked']:
        save_name = f"masked_{card_type}.png"
        decoded_data = base64.b64decode(r['doc_b64_masked'])
        np_data = np.frombuffer(decoded_data, np.uint8)
        img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(save_name, img)
        return f"Masked document saved as {save_name}"
    else:
        return f"Unable to find given number in the image for {card_type} :/ (try brut mode)"

def hit_api_brut_mask(card_type, input_name, output_name):
    img_bytes = to_image_string(input_name)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:8001'
    if card_type == 'aadhaar':
        url = addr + '/api/brut_mask'
    elif card_type == 'pan':
        url = addr + '/api/brut_mask_pan'
    response = requests.post(url, json={"doc_b64": img_bytes}, headers=headers)
    r = json.loads(response.text)
    save_name = output_name
    decoded_data = base64.b64decode(r['doc_b64_brut_masked'])
    np_data = np.frombuffer(decoded_data, np.uint8)
    img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    cv2.imwrite(save_name, img)
    return f"Masked document saved as {save_name}"

def hit_api_sample_pipe(card_type, input_name, output_name, brut=False):
    img_bytes = to_image_string(input_name)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:8001'
    if card_type == 'aadhaar':
        url = addr + '/api/sample_pipe'
    elif card_type == 'pan':
        url = addr + '/api/sample_pipe_pan'
    response = requests.post(url, json={"doc_b64": img_bytes, "brut": brut}, headers=headers)
    r = json.loads(response.text)
    if r['is_masked']:
        save_name = output_name
        decoded_data = base64.b64decode(r['doc_b64_masked'])
        np_data = np.frombuffer(decoded_data, np.uint8)
        img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(save_name, img)
        print("Execution Mode =>", r['mode_executed'])
        if r['mode_executed'] == "OCR-MASKING":
            print(f"{card_type.capitalize()} List =>", r[f'{card_type}_list'])
            print(f"Validated {card_type.capitalize()} list =>", r[f'valid_{card_type}_list'])
        return f"Masked document saved as {save_name}"
    else:
        print("Execution Mode =>", r['mode_executed'])
        print("Error =>", r['error'])
        return f"Unable to find given number in the image for {card_type} :/ (try brut mode)"

# Usage examples

# Validate PAN card number
pan_number = 'ABCDE1234F'
print(hit_api_validate('pan', pan_number))

# Extract PAN number from an image
pan_image = 'pan_card.jpg'  # Replace with your PAN card image
print(hit_api_extract('pan', pan_image))

# Mask PAN number in an image
pan_image = 'pan_card.jpg'  # Replace with your PAN card image
pan_number_list = ['ABCDE1234F']
print(hit_api_mask('pan', pan_image, pan_number_list))

# Brut mask PAN numbers in an image
pan_image = 'pan_card.jpg'  # Replace with your PAN card image
pan_masked_image = 'masked_pan_card.png'  # Replace with your desired output file name
print(hit_api_brut_mask('pan', pan_image, pan_masked_image))

# Full pipeline for PAN card processing
pan_image = 'pan_card.jpg'  # Replace with your PAN card image
pan_masked_image = 'masked_pan_card.png'  # Replace with your desired output file name
print(hit_api_sample_pipe('pan', pan_image, pan_masked_image, brut=True))

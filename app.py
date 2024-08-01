from flask import Flask, request, jsonify, render_template
import replicate
from functools import wraps

app = Flask(__name__)

import replicate
import os

import traceback
import sys

def require_api_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split('Bearer ')[1]
            os.environ["REPLICATE_API_TOKEN"] = "r8_OUgsjAHZtSSQeGjbSUs15wlF4GCcdsP0hgm4L"
            return f(*args, **kwargs)
        return jsonify({"error": "Invalid or missing API token"}), 401
    return decorated


# runs vton as many times as needed to apply each article of clothing
def run_vton(input, garm_list, category_list):

    if (not garm_list) or (not category_list):
        return input['human_img']

    input['garm_img'] = garm_list[0]
    input['category'] = category_list[0]

    garm_list.remove(garm_list[0])
    category_list.remove(category_list[0])

    print()
    print("Running vton")

    print()
    print(input['garm_img'])
    print(input['human_img'])

    vton_output = replicate.run( 
        "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f", 
        input=input
    )

    print()
    print("vton done")

    input['human_img'] = vton_output

    return run_vton(input, garm_list, category_list)


@app.route('/', methods=['GET'])
def index():
    os.environ["REPLICATE_API_TOKEN"] = "r8_OUgsjAHZtSSQeGjbSUs15wlF4GCcdsP0h"
    return render_template('index.html')

@app.route('/generate_3d_from_vton', methods=['POST', 'GET'])
def generate_3d_from_vton(): 
    
    try:

        data = request.get_json(force=True, cache=False)

        api_token = data.get('apiToken')
        if not api_token:
            return jsonify({"error": "API token is required"}), 400

        print("Received new request for /generate_3d_from_vton", file=sys.stderr)

        os.environ["REPLICATE_API_TOKEN"] = api_token
        
        # Validate that required fields are present
        if 'human_img' not in data or 'upper_body_img' not in data or 'lower_body_img' not in data:
            return jsonify({"error": "Missing required fields: 'human_img' and/or 'garm_img'"}), 400
        

        # First model: cuuupid/idm-vton
        vton_input = {
            "human_img": data.get('human_img'),
            "crop": True,
            "seed": data.get('seed', 30),
            "steps": 40,
            "mask_only": False,
            "force_dc": False,
            "garment_des": ''
        }

        garm_list = [data.get('lower_body_img'), data.get('upper_body_img')]
        category_list = ['lower_body', 'upper_body']

        vton_output = run_vton(vton_input, garm_list, category_list)

        generated_image_url = vton_output[0] if isinstance(vton_output, list) else vton_output
        
        print("Generated image URL:", generated_image_url)

        # Second model: deepeshsharma2003/3dmg
        dmg_input = {
            "seed": data.get('seed', 42),
            "image_path": generated_image_url,
            "export_video": True,
            "sample_steps": 300,
            "export_texmap": False,
            "remove_background": True
        }

        print("Running 3DMG model...")
        dmg_output = replicate.run(
            "deepeshsharma2003/3dmg:476f025230580cb41ffc3b3d6457965f968c63d1db4a0737bef338a851eb62d6",
            input=dmg_input
        )
    
        print(dmg_output[0])
        print(dmg_output[1])
        print(dmg_output[2])

        return jsonify({"result": dmg_output[1]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"}), 200


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
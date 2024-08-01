import streamlit as st
import requests
from PIL import Image
import base64

# Set the API endpoints
VTON_API_ENDPOINT = "http://localhost:5000/generate_3d_from_vton"
IMGBB_API_ENDPOINT = "https://api.imgbb.com/1/upload"
IMGBB_API_KEY = "bccd65ab8da85ebc87c6a9d81e41d1de"  # Replace with your ImgBB API key

def upload_to_imgbb(image_file):
    img_bytes = image_file.getvalue()
    base64_image = base64.b64encode(img_bytes).decode('utf-8')
    
    payload = {
        "key": IMGBB_API_KEY,
        "image": base64_image,
    }
    
    response = requests.post(IMGBB_API_ENDPOINT, payload)
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        st.error(f"Failed to upload image to ImgBB. Status code: {response.status_code}")
        return None

st.title("Virtual Try-On and 3D Model Generator")

# Input for API token
api_token = st.text_input("Enter your Replicate API token. Sign up for ReplicateAI and obtain a token if you do not have one already:", type="password")

# File upload for human image
human_img_file = st.file_uploader("Upload human image", type=["png", "jpg", "jpeg"])

# File upload for upper body garment
upper_body_img_file = st.file_uploader("Upload upper body garment image", type=["png", "jpg", "jpeg"])

# File upload for lower body garment
lower_body_img_file = st.file_uploader("Upload lower body garment image", type=["png", "jpg", "jpeg"])

# Input for seed
seed = st.number_input("Enter seed value (optional):", value=30, step=1)

if st.button("Generate 3D Model"):
    if not api_token:
        st.error("Please enter your VTON API token.")
    elif not human_img_file or not upper_body_img_file or not lower_body_img_file:
        st.error("Please upload all required images.")
    else:
        # Upload images to ImgBB
        with st.spinner("Uploading images..."):
            human_img_url = upload_to_imgbb(human_img_file)
            upper_body_img_url = upload_to_imgbb(upper_body_img_file)
            lower_body_img_url = upload_to_imgbb(lower_body_img_file)

        if human_img_url and upper_body_img_url and lower_body_img_url:
            # Prepare the data for the VTON API
            data = {
                "apiToken": api_token,
                "human_img": human_img_url,
                "upper_body_img": upper_body_img_url,
                "lower_body_img": lower_body_img_url,
                "seed": seed,
            }

            # Make the API request to the VTON service
            with st.spinner("Generating 3D model..."):
                try:
                    response = requests.post(VTON_API_ENDPOINT, json=data)
                    response.raise_for_status()  # Raise an exception for bad status codes
                except requests.exceptions.RequestException as e:
                    st.error(f"Error communicating with the VTON API: {str(e)}")
                else:
                    if response.status_code == 200:
                        result = response.json().get("result")
                        if result:
                            st.success("3D model generated successfully!")
                            st.video(result)
                        else:
                            st.error("The API response did not contain a result.")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error occurred')}")
        else:
            st.error("Failed to upload one or more images to ImgBB.")

# Preview uploaded images
if human_img_file:
    st.image(human_img_file, caption="Uploaded Human Image", use_column_width=True)
if upper_body_img_file:
    st.image(upper_body_img_file, caption="Uploaded Upper Body Garment", use_column_width=True)
if lower_body_img_file:
    st.image(lower_body_img_file, caption="Uploaded Lower Body Garment", use_column_width=True)

st.markdown("---")
st.markdown("Made with ❤️ by Your Name")
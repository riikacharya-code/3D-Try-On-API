import requests
import json
import uuid


def send_request_to_api(human_img, upper_body_img, lower_body_img, api_token, seed=42, crop=False):

    url = "http://192.168.1.8:5000/generate_3d_from_vton"

    data = {
        "human_img": human_img,
        "upper_body_img": upper_body_img,
        "lower_body_img": lower_body_img,
        "seed": seed,
        "force_dc": False,
        "crop": crop,
        "request_id": str(uuid.uuid4()),
        'apiToken': api_token
    }

    headers = {
        'Content-Type': 'application/json', 
        'Authorization': f'Bearer {api_token}',
        'Cache-Control': 'no-cache'
    }
    
    print(json.dumps(data))

    try:
        print("Sending request to API...")
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response'):
            print(f"Error response content: {e.response.text}")
        return None


def test_api_connection():
    url = "http://192.168.1.8:5000/test"
    try:
        response = requests.get(url)
        print(f"Test response status code: {response.status_code}")
        print(f"Test response content: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Test request failed: {e}")




# Call this function before your main request
#test_api_connection()

if __name__ == "__main__":

    '''
    Choose 1 upper body garment and 1 lower body garment. 
    Make sure the human image has most of their whole body. 
    An image with mostly only their legs will not work and an image with 
    mostly their upper body will not work as well for the lower body garment.

    Sign up for a Replicate account and get your own API key.

    Some examples of input clothes are in the files 'upper_body.txt' and 'lower_body.txt'.
    '''

    human_img = "https://time.com/shopping/static/07879e7b8e0ca5c988fadbc8ee6548e0/ca7ff/best-womens-dress-pants-for-work.jpg"
    upper_body_img = "https://www.3wisemen.co.nz/media/catalog/product/c/6/c60_2311288_1.jpg?optimize=low&bg-color=255,255,255&fit=bounds&height=700&width=700&canvas=700:700"
    lower_body_img = "https://truewerk.com/cdn/shop/files/t2_werkpants_mens_sand_flat_lay_8ef2f98e-2d28-4d79-9661-ccab84a67cf3.jpg?v=1701119637&width=2400"
    seed = 42

    api_token = "r8_OUgsjAHZtSSQeGjbSUs15wlF4GCcdsP0hgm4L" #replace with your own API key

    result = send_request_to_api(human_img, upper_body_img, lower_body_img, api_token, seed)
    print(result)
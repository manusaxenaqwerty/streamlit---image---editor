import streamlit as st
import base64
import requests
import json
from io import BytesIO
from PIL import Image
import time 


API_KEY = ""
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"

st.set_page_config(page_title="Gemini Image Generator & Editor", layout="centered")

st.title("🎨 Gemini Image Generator & Editor")
st.markdown("Enter a prompt to generate a new image, or upload an image and a prompt to edit it.")


prompt = st.text_area("Enter your prompt:", "A futuristic city skyline at sunset, cyberpunk style, high detail")


uploaded_file = st.file_uploader("Upload an image to edit (optional):", type=["png", "jpg", "jpeg"])


if st.button("Generate/Edit Image"):
    if not prompt:
        st.error("Please enter a prompt to generate or edit the image.")
    else:
        st.info("Generating your image... please wait.")
        
  
        payload = {}
        if uploaded_file is not None:
            
            image_bytes = uploaded_file.getvalue()
            
      
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            
          
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inlineData": {
                                    "mimeType": uploaded_file.type,
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"]
                }
            }
        else:
          
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"]
                }
            }

        headers = {
            "Content-Type": "application/json"
        }
        
        try:
        
            max_retries = 3
            retries = 0
            while retries < max_retries:
                try:
                    response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
                    response.raise_for_status() 
                    break 
                except requests.exceptions.RequestException as e:
                    retries += 1
                    if retries < max_retries:
                        st.warning(f"Request failed, retrying... ({retries}/{max_retries})")
                       
                        time.sleep(2 ** retries)
                    else:
                        st.error(f"Failed to connect to the API after multiple retries. Error: {e}")
                        st.stop()
            
           
            response_json = response.json()
            candidate = response_json.get("candidates", [])[0]
            
       
            image_data = None
            for part in candidate["content"]["parts"]:
                if "inlineData" in part and "image" in part["inlineData"]["mimeType"]:
                    image_data = part["inlineData"]["data"]
                    break
            
            if image_data:
             
                image_bytes = base64.b64decode(image_data)
                image_stream = BytesIO(image_bytes)
                
                
                pil_image = Image.open(image_stream)
                st.image(pil_image, caption="Generated/Edited Image", use_column_width=True)
                
            else:
                st.error("No image data received from the API.")
                st.json(response_json) 
                
        except json.JSONDecodeError:
            st.error("Failed to decode JSON from the API response.")
            st.write(response.text)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

import google.generativeai as genai 
import PIL.Image
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from io import BytesIO
from datetime import datetime
import streamlit as st
import base64
import json

load_dotenv()

my_key_stabilityai = os.getenv("stabilityai_apikey")

### SD XL Image Generation 

def generate_image_with_SD(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {my_key_stabilityai}",
    }

    body = {
        "steps": 50,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "cfg_scale": 8,
        "samples": 1,
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            },
            {
                "text": "blurry, pointless, obscure, peculiar",
                "weight": -1
            }
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    data = response.json()

    artifacts = data.get("artifacts", [])

    image_bytes = base64.b64decode(artifacts[0]["base64"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./img/generated_image_{timestamp}.png"

    if not os.path.exists("./img"):
        os.makedirs("./img")

    with open(filename, "wb") as file:
        file.write(image_bytes)

    return filename


# ### DALL-E 3 Image Generation 

# load_dotenv()

# my_key_openai=os.getenv("openai_apikey")

# client= OpenAI(api_key=my_key_openai)

# def generate_image_with_dalle(prompt):

#     AI_Response=client.images.generate(
#         model="dall-e-2",
#         size="1024x1024",
#         quality="hd",
#         n=1,
#         response_format="url",
#         prompt=prompt   
#     )

#     image_url=AI_Response.data[0].url

#     response=requests.get(image_url)
#     image_bytes=BytesIO(response.content)

#     timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename=f"./img/generated_image_{timestamp}.png"

#     if not os.path.exists("./img"):
#         os.makedirs("./img")

#     with open(filename,"wb") as file:
#         file.write(image_bytes.getbuffer())

#     return filename

my_key_google= os.getenv("google_apikey")

genai.configure(
    api_key=my_key_google
)

def gemini_vision_with_local_file(image_path, prompt):

    multimodality_prompt= f"""I would like you to recreate this image I sent you, with some additional instructions. 
    First, I would like you to describe the image in great detail. 
    Then, I will use the resulting text to create a visual using an artificial intelligence model. 
    Therefore, while finalizing your answer, I would like you to take into consideration that this is an input, 
    a prompt, that will be used to produce an image. Here is additional guidance: {prompt}
    """

    client=genai.GenerativeModel(model_name="gemini-pro-vision")

    source_image=PIL.Image.open(image_path)

    AI_Response=client.generate_content(
        [
            multimodality_prompt,
            source_image
        ]
    )

    AI_Response.resolve()

    return AI_Response.text


# def generate_image(image_path,prompt):

#     image_based_prompt= gemini_vision_with_local_file(image_path=image_path,prompt=prompt)

#     filename= generate_image_with_dalle(prompt=image_based_prompt)

#     return filename

def generate_image(image_path,prompt):

    image_based_prompt= gemini_vision_with_local_file(image_path=image_path,prompt=prompt)

    filename= generate_image_with_SD(prompt=image_based_prompt)

    return filename

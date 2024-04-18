from hugchat import hugchat
from hugchat.login import Login
from dotenv import dotenv_values
import time


def generate_phrases(prompts):
    # Load environment variables inside the function
    secrets = dotenv_values('hf.env')
    hf_email = secrets['EMAIL']
    hf_pass = secrets['PASS']

    # Hugging Face Login
    sign = Login(hf_email, hf_pass)
    cookies = sign.login()
    
    # Add a delay
    time.sleep(2)

    # Create ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    
    responses = []
    for prompt in prompts:
        response = chatbot.chat(prompt)
        responses.append(response)
    
    return responses

##prompt = "donne moi cinq phrases sur le sport"
##response = generate_response(prompt, hf_email, hf_pass)
##print(response)
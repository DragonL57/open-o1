import os
from core.llms import LLM
from dotenv import load_dotenv
from typing import Annotated, Optional
# from function_schema import Doc
from core.llms.utils import user_message_with_images

load_dotenv('../.global_env')

# def get_weather(
#     city: Annotated[str, "The city to get the weather for"], # <- string value of Annotated is used as a description
#     unit: Annotated[Optional[str], "The unit to return the temperature in"] = "celcius",
# ) -> str:
#     """Returns the weather for the given city."""
#     return f"Weather for {city} is 20°C"


# def get_distance(city1: Annotated[str, 'city to start journey from'], city2: Annotated[str, 'city where journey ends']) -> float:
#     ''' Returns distance between two cities '''
#     return f"{city1} --- {city2}: 10 KM"

# tools = {"get_weather": get_weather, 'get_distance':get_distance}

# models= [
#     ('gemini/gemini-1.5-flash', 'GEMINI_API_KEY'),
#     ('groq/llava-v1.5-7b-4096-preview', 'GROQ_API_KEY')
# ]

# model , api_key = models[0]
# api_key = os.getenv(api_key)

# llm = LLM(api_key=api_key, model=model)

# messages = [
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     # {"role": "user", "content": "whats weather in new york, what is distance between new york and las vegas"},
# # user_message_with_images(
# #     'explain this image',
# #     file_path_list = ['./hehe.jpg'],
# #     max_size_px=512, 
    
# # )

# ]

# response = llm.chat(messages)

# print('response: ', response)
from app.app import main

if __name__ == '__main__':
    main()

from calendar import c
from dataclasses import dataclass
from math import exp
from webbrowser import get
from litellm.types.utils import ModelResponse
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from app.utils import generate_answer, dict_to_markdown
from core.types import ThoughtStepsDisplay, ThoughtSteps, BigMessage , Message
from .app_config import InputConfig, ENV_FILE_PATH, CONFIG_FILE_PATH
from core.llms.base_llm import BaseLLM
from core.llms.litellm_llm import LLM
from core.llms.utils import user_message_with_images
from PIL import Image
from core.prompts.think_mark_think import SYSTEM_PROMPT

st.set_page_config(page_title="Open-o1", page_icon="🧠", layout="wide")
st.title('Open-O1')
st.write('Welcome to Open-O1!')

def config_sidebar(config:InputConfig) -> InputConfig:
    st.sidebar.header('Configuration')
    model_name =    st.sidebar.text_input('Enter Model Name: e.g. provider/model-name',value=config.model_name, placeholder='openai/gpt-3.5-turbo')
    model_api_key = st.sidebar.text_input('Enter API Key: ',type='password',value=config.model_api_key, placeholder='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    max_tokens =    st.sidebar.number_input('Enter Max Tokens per Thought: ',value=config.max_tokens, min_value=1)
    max_steps =     st.sidebar.number_input('Enter Max Thinking Steps: ',value=config.max_steps, min_value=1, step=1, ) 
    temperature =   st.sidebar.number_input('Enter Temperature: ',value=config.temperature, min_value=0.0, step=0.1, max_value=10.0)
    timeout =       st.sidebar.number_input('Enter timeout(seconds): ',value=config.timeout, min_value=0.0,step = 1.0)
    sleeptime =     st.sidebar.number_input('Enter Sleep Time(seconds): (time bw requests to avoid rate limit)',value=config.sleeptime, min_value=0.0, step = 1.0) 
    
    config.model_name = model_name
    config.model_api_key = model_api_key
    config.max_tokens = max_tokens
    config.max_steps = max_steps
    config.temperature = temperature
    config.timeout = timeout
    config.sleeptime = sleeptime

    if st.sidebar.button('Save config'):
        config.save(env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH)
        st.sidebar.success('Config saved!')
        
    return config

def load_llm(config:InputConfig, tools=None) -> BaseLLM:
    return LLM(api_key=config.model_api_key, model=config.model_name, tools=tools)

    
def image_buffer_to_pillow_image(image_buffer:UploadedFile) -> Image.Image:
    return Image.open(image_buffer)


def process_user_input(user_input:str, image:Image.Image=None)->dict:
    if image:
        message = [user_message_with_images(user_msg_str=user_input, images=[image])] 
    else:
        message = [{"role": "user", "content": user_input}]
    return message



    
def main():
    
    config = InputConfig.load(env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH)    
    config = config_sidebar(config=config)
    llm = load_llm(config)

    current_tab = ''
    
    current_tab='o1_tab'
    messages_attr_name = f"{current_tab}_messages"
    big_message_attr_name = f"{current_tab}_big_messages"
    

    clear_chat_bt = st.sidebar.button('Clear Chat')
    if clear_chat_bt:
        delattr(st.session_state, messages_attr_name)


    message_attr = set_and_get_state_attr(messages_attr_name, default_value=[])
    big_message_attr = set_and_get_state_attr(big_message_attr_name, default_value=[])
    
    # this prints the older messages
    for message in big_message_attr:
        with st.chat_message(message.role):
            
            for thought in message.thoughts:
                print_thought(thought.to_thought_steps_display(), is_final=False)

            if message.content:
                if message.role == 'user':
                    st.markdown(message.content)
                else:
                    print_thought(message.to_thought_steps_display(), is_final=True)

            
    
    if prompt := st.chat_input("What is up bro?"):
        big_message_attr.append(BigMessage(role="user", content=prompt, thoughts=[])) 
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            messages = [{
                "role": "system",
                "content": SYSTEM_PROMPT
            }]
            
            messages += [m.to_message() for m in big_message_attr]
            
            thoughts = []
            
            #add json keyword in user message , helps in json output
            for message in messages:
                if message["role"] == "user":
                    message["content"] = f"{message['content']}, json format"
            
            
            for num,step in enumerate(generate_answer(
                messages=messages, 
                max_steps=config.max_steps, 
                stream=False, 
                max_tokens=config.max_tokens, 
                temperature=config.temperature, 
                sleeptime=config.sleeptime,
                timeout=config.timeout, 
                llm=llm,
                response_format={ "type": "json_object" }
                
                ),1):

                thoughts.append(step)
                print_thought(step.to_thought_steps_display(), is_final=False)

            last_step = thoughts.pop()
            message_attr.append(BigMessage(
                role="assistant", 
                content=last_step, 
                thoughts=thoughts
            ))
            # st.markdown(dict_to_markdown(step.model_dump()))


    
def set_and_get_state_attr(attr_name:str, default_value:any=None) -> any:
    if attr_name not in st.session_state:
        setattr(st.session_state, attr_name, default_value)
    return getattr(st.session_state, attr_name)


def print_thought(thought:ThoughtStepsDisplay, is_final:bool=False):
    if is_final:
       st.markdown(thought.md())
    else:
        st.markdown(f'\n```json\n{thought.model_dump_json()}\n```\n', unsafe_allow_html=True) 
        

        
    
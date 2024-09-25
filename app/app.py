import time
import streamlit as st
from app.utils import generate_answer, load_llm
from core.types import ThoughtStepsDisplay, BigMessage 
from .app_config import InputConfig, ENV_FILE_PATH, CONFIG_FILE_PATH
from core.prompts.cot import SYSTEM_PROMPT




def config_sidebar(config:InputConfig) -> InputConfig:
    st.sidebar.header('Configuration')
    model_name =    st.sidebar.text_input('Model Name: e.g. provider/model-name',value=config.model_name, placeholder='openai/gpt-3.5-turbo')
    model_api_key = st.sidebar.text_input('API Key: ',type='password',value=config.model_api_key, placeholder='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    max_tokens =    st.sidebar.number_input('Max Tokens per Thought: ',value=config.max_tokens, min_value=1)
    max_steps =     st.sidebar.number_input('Max Thinking Steps: ',value=config.max_steps, min_value=1, step=1, ) 
    temperature =   st.sidebar.number_input('Temperature: ',value=config.temperature, min_value=0.0, step=0.1, max_value=10.0)
    timeout =       st.sidebar.number_input('Timeout(seconds): ',value=config.timeout, min_value=0.0,step = 1.0)
    sleeptime =     st.sidebar.number_input('Sleep Time(seconds)',value=config.sleeptime, min_value=0.0, step = 1.0, help='Time between requests to avoid hitting rate limit')  
    force_max_steps = st.sidebar.checkbox('Force Max Steps', value=config.force_max_steps, help="If checked, will generate given number of max steps. If not checked, assistant can stop at few step thinking it has the right answer.") 
    
    config.model_name = model_name
    config.model_api_key = model_api_key
    config.max_tokens = max_tokens
    config.max_steps = max_steps
    config.temperature = temperature
    config.timeout = timeout
    config.sleeptime = sleeptime
    config.force_max_steps = force_max_steps
    

    if st.sidebar.button('Save config'):
        config.save(env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH)
        st.sidebar.success('Config saved!')
        
    return config


    
def main():
    st.set_page_config(page_title="Open-o1", page_icon="🧠", layout="wide")
    st.title('Open-O1')
    st.write('Welcome to Open-O1!')

    
    config = InputConfig.load(env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH)    
    config = config_sidebar(config=config)
    llm = load_llm(config)

    
    current_tab='o1_tab'
    big_message_attr_name = f"{current_tab}_big_messages"
    

    clear_chat_bt = st.sidebar.button('Clear Chat')
    if clear_chat_bt:
        delattr(st.session_state, big_message_attr_name)


    big_message_attr = set_and_get_state_attr(big_message_attr_name, default_value=[])
    
    # this prints the older messages
    for message in big_message_attr:
        with st.chat_message(message.role):
            
            for thought in message.thoughts:
                print_thought(thought, is_final=False)

            if message.content:
                if message.role == 'user':
                    st.markdown(message.content)
                else:
                    print_thought(message.content, is_final=True)

            
    
    if user_input := st.chat_input("What is up bro?"):
        big_message_attr.append(BigMessage(role="user", content=user_input, thoughts=[])) 
        
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            
            
            thoughts = []
            messages = [message.to_message() for message in big_message_attr]
            
            messages[-1]['content'] += ", json format" #add json keyword in user message , helps in json output
            
            start_time = time.time()
            
            with st.status("Thinking...", expanded=True) as status:

                for step in generate_answer(
                    messages=messages, 
                    max_steps=config.max_steps, 
                    stream=False, 
                    max_tokens=config.max_tokens, 
                    temperature=config.temperature, 
                    sleeptime=config.sleeptime,
                    timeout=config.timeout, 
                    llm=llm,
                    force_max_steps=config.force_max_steps,
                    response_format={ "type": "json_object" }
                    
                    ):

                    thoughts.append(step)

                    st.write(step.md())
                    # add breakline after each step
                    st.markdown('---')
                    status.update(label=step.step_title, state="running", expanded=False)
                    

                status.update(
                    label=f"Thought for {time.time()-start_time:.2f} seconds", state="complete", expanded=False
                )

            last_step = thoughts.pop()
            print_thought(last_step, is_final=True)

            big_message_attr.append(BigMessage(
                role="assistant", 
                content=last_step, 
                thoughts=thoughts
            ))


    
def set_and_get_state_attr(attr_name:str, default_value:any=None) -> any:
    if attr_name not in st.session_state:
        setattr(st.session_state, attr_name, default_value)
    return getattr(st.session_state, attr_name)


def print_thought(thought:ThoughtStepsDisplay, is_final:bool=False):
    if is_final:
       st.markdown(thought.md())
    else:
        # st.markdown(f'\n```json\n{thought.model_dump_json()}\n```\n', unsafe_allow_html=True) 
        with st.expander(f'{thought.step_title}'):
            st.markdown(thought.md())

        
    
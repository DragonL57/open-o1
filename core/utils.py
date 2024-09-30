

import re
import json
import ast
from pydantic import ValidationError
from termcolor import colored

def extract_code_block(text):
    code_block = re.findall(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    
    if code_block:
        try:
            return [ast.literal_eval(block) for block in code_block]
        except (SyntaxError, ValueError) as e:
            return f"Error parsing code block: {e}"
    return None



def extract_code_block(text):
    code_block = re.findall(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    
    if code_block:
        try:
            return [json.loads(block) for block in code_block]
        except json.JSONDecodeError:
            return None
    return None

# def fallback_extract(text, expected_keys):
#     fallback_dict = {}
#     for i, key in enumerate(expected_keys):
#         match = re.search(rf'"{key}"\s*:\s*([^\s,]+)', text)
#         if match:
#             value = match.group(1).strip('"').strip(',')
#             if value.isdigit():
#                 fallback_dict[key] = int(value)
#             elif re.match(r'^\{.*\}$', value):  # Detect dictionary structure
#                 try:
#                     fallback_dict[key] = json.loads(value)
#                 except json.JSONDecodeError:
#                     fallback_dict[key] = value  # Leave it as a string if malformed
#             else:
#                 fallback_dict[key] = value
#         else:
#             fallback_dict[key] = None  # If the key is not found, set it to None
#     return fallback_dict

def fallback_extract(text, expected_keys):
    fallback_dict = {}
    pattern = r'"({})"\s*:\s*(.*?)(?="(?:{})"|\Z)'.format(
        '|'.join(re.escape(key) for key in expected_keys),
        '|'.join(re.escape(key) for key in expected_keys)
    )
    
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        key, value = match.groups()
        value = value.strip().rstrip(',').strip()
        
        if value.isdigit():
            fallback_dict[key] = int(value)
        elif value.lower() in ['true', 'false']:
            fallback_dict[key] = value.lower() == 'true'
        elif re.match(r'^\{.*\}$', value):  # Detect dictionary structure
            try:
                fallback_dict[key] = json.loads(value)
            except json.JSONDecodeError:
                fallback_dict[key] = value  # Leave it as a string if malformed
        else:
            # Remove surrounding quotes if present
            fallback_dict[key] = value.strip('"')
    
    # Add any missing keys with None value
    for key in expected_keys:
        if key not in fallback_dict:
            fallback_dict[key] = None
    
    return fallback_dict

# Main function to handle parsing with fallback
def parse_with_fallback(text, pydantic_class):
    # Extract expected keys from the Pydantic class
    expected_keys = list(pydantic_class.__fields__.keys())
    
    # First try to extract clean JSON blocks
    parsed_blocks = extract_code_block(text)
    
    if parsed_blocks:
        # Validate and return parsed data
        try:
            classes = [pydantic_class(**block) for block in parsed_blocks]
            print(colored('used code block', 'red'))
            print(colored('Got this: {0}'.format(classes[0]), 'red'))
            print(colored('from this: {0}'.format(text), 'cyan'))
            
            return classes[0]
        except ValidationError as e:
            print("Validation error:", e)
    
    # Fallback to manually extracting key-value pairs
    fallback_data = fallback_extract(text, expected_keys)
    
    try:
        # Try to validate the fallback data with the Pydantic class
        print(colored('used fallback', 'red'))
        print(colored('Got this: {0}'.format(fallback_data), 'red'))
        print(colored('from this: {0}'.format(text), 'cyan'))

        return pydantic_class(**fallback_data)
    except ValidationError as e:
        return None

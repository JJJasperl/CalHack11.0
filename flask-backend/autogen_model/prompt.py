import pandas as pd

TERMINATE_CODE = "terminate:pink_drink_is_tasteless"

ENTRYPOINT_AGENT_SYSTEM_MESSAGE = (
    "You are the Entry Point Agent. Your role is to receive audio from customers, "
    "initiate communication with the Transcription Agent to convert audio to text, "
    "send the text to the Query Agent to match it menu items.\n"
    #"After receiving results, you must inform the customer of the order and handle "
    #"clarifications as needed. "
    "Maintain context and coordinate the overall flow of the interaction."
)

TRANSCRIPTION_AGENT_SYSTEM_MESSAGE = (
    "You are the Transcription Agent. Your role is to convert audio into text. "
    "When contacted by the Entry Point Agent, you will receive audio data, "
    "convert it to text, and send the text back.\n"
    "Only focus on converting audio to text. "
    "Output {TERMINATE_CODE} after you send the converted text."
)

TRANSCRIPTION_SUMMARY_PROMPT = '''Generate a summary of the conversation in JSON format. The JSON should include two fields:
1. "transcription": the text that was transcribed from the customer's audio.
Ensure the output is formatted correctly and includes all relevant details. Here is an example format to follow:
{
    "transcription": "transcribed text here"
}
'''

TRANSCRIPTION_AGENT_PROMPT = (
    "Please convert the following audio input into text."
)

CHECK_AGENT_SYSTEM_MESSAGE = (
    "You are the Check Agent. Your role is to check if the customer is satisfied with its order. "
    "If they say anything such as 'that's all' or 'that's it' or 'checkout', you should inform the Entry Point Agent that the order is complete. "
    "If the customer asks for changes or has any other requests, you should inform the Query Agent to handle the request."
)

CHECK_AGENT_PROMPT = (
    "Please check if the customer is satisfied with the order or if they have any other requests."    
)

CHECK_SUMMARY_PROMPT = '''Output 'the user is satisfied' if the customer is satisfied with the order and 'the user is not satisfied' if they have any other requests. Do not output any other information.'''

def get_check_prompt(user_input):
    return f"Please check if the customer is satisfied with the order or if they have any other requests.\n\nThe user query is: {user_input}"

QUERY_AGENT_SYSTEM_MESSAGE = (f"""If the user is satisfied with the order, please inform the Entry Point Agent that the order is complete and do not do anything else.
    Do the following if the user is not satisfied with the order:
    You are the Query Agent. Your role is to take text input from the Entry Point Agent
    and match it with valid items from the menu.
    Given the following menu data:
    {pd.read_csv("../Assets/Data/selectedColumn.csv")}

    Output {TERMINATE_CODE} after you send the items and quantity the customer ordered.
    """
)

QUERY_AGENT_PROMPT = (
    "Please match the following customer order query with valid menu items and return the results."
)

QUERY_SUMMARY_PROMPT = '''Generate a summary of the conversation in JSON format. The JSON should include three fields:
1. "transcription": the text that was transcribed from the customer's audio.
2. "items": a dictionary where the keys are the names of the menu items ordered. Each item should have a nested dictionary with four fields:
    - "quantity": the number of each item ordered. If the user mean to cancel order, the quantity should be negative.
    - "size": the size of the item.
    - "price": the price of the item.
    - "comment": other relevant information.
    If the user is satisfied with the order, then this field should be empty.
3. "satisfied": a boolean value indicating whether the user is satisfied with the order. 
Ensure the output is formatted correctly and includes all relevant details. Here is an example format to follow:
{
    "transcription": "transcribed text here",
    "items": {
        "Item1": {
            "quantity": quantity1,
            "size": "size1",
            "price": price1,
            "comment": "comment1"
        },
        "Item2": {
            "quantity": quantity2,
            "size": "size2",
            "price": price2,
            "comment": "comment2"
        },
        ...
    }
    "satisfied": true/false
}
'''
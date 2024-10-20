from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import math
from prompt import TERMINATE_CODE
from util import get_recipient_prompt, get_system_message, get_summary_prompt

def register_function(sender, receiver, func, description):
    sender.register_for_execution()(func)
    receiver.register_for_llm(description=description)(func)

def main(audio_query):
    # LLM config
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # define agents
    entrypoint_agent = ConversableAgent(name="Entrypoint_Agent", 
                                        system_message=get_system_message("entrypoint"), 
                                        llm_config=llm_config,
                                        is_termination_msg=lambda x: (x.get("content", "").find(TERMINATE_CODE) >= 0 if x.get("content", "") != None else False),
                                        human_input_mode="NEVER")
    # transcription_aegnt = ConversableAgent(name="Transcription_Agent",
    #                                        system_message=get_system_message("transcription"),
    #                                        llm_config=llm_config,
    #                                        human_input_mode="NEVER")
    query_agent = ConversableAgent(name="Transcription_Agent",
                                   system_message=get_system_message("query"),
                                   llm_config=llm_config,
                                   human_input_mode="NEVER")
    # output_agent = ConversableAgent(name="Transcription_Agent",
    #                                 system_message=get_system_message("output"),
    #                                 llm_config=llm_config,
    #                                 human_input_mode="NEVER")
    
    # register functions
    # TODO

    # workflow
    result = entrypoint_agent.initiate_chats(
        [
            # {
            #     "recipient": transcription_aegnt,
            #     "message": get_recipient_prompt("transcription"),
            #     "max_turns": 3,
            #     "summary_method": "reflection_with_llm",
            #     "summary_args": {
            #         "summary_prompt": get_summary_prompt("transcription")
            #     }
            # },
            {
                "recipient": query_agent,
                "message": get_recipient_prompt("query"),
                "max_turns": 3,
                "summary_method": "reflection_with_llm",
                "summary_args": {
                    "summary_prompt": get_summary_prompt("query")
                }
            },
            # {
            #     "recipient": output_agent,
            #     "message": get_recipient_prompt("output"),
            #     "max_turns": 3,
            #     "summary_method": "reflection_with_llm",
            #     "summary_args": {
            #         "summary_prompt": get_summary_prompt("output")
            #     }
            # }
        ]
    )
    print(result[-1].summary)
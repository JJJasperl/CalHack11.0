from autogen import ConversableAgent
import os
from autogen_model.prompt import TERMINATE_CODE
from autogen_model.util import get_system_message, get_summary_prompt, get_recipient_prompt
from autogen_model.menu_query import generatePrompting


def register_function(sender, receiver, func, description):
    sender.register_for_execution()(func)
    receiver.register_for_llm(description=description)(func)


def return_menu_query_information(user_input):

    # user_input = "Can I have a large double cheeseburger combo meal"

    # LLM config
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # define agents
    entrypoint_agent = ConversableAgent(name="Entrypoint_Agent",
                                        system_message=get_system_message("entrypoint"),
                                        llm_config=llm_config,
                                        is_termination_msg=lambda x: (x.get("content", "").find(TERMINATE_CODE) >= 0 if x.get("content", "") != None else False),
                                        human_input_mode="NEVER")
    check_agent = ConversableAgent(name="Check_Agent",
                                   system_message=get_system_message("check"),
                                   llm_config=llm_config,
                                   human_input_mode="NEVER")
    query_agent = ConversableAgent(name="Transcription_Agent",
                                   system_message=get_system_message("query"),
                                   llm_config=llm_config,
                                   human_input_mode="NEVER")

    # workflow
    result = entrypoint_agent.initiate_chats(
        [
            {
                "recipient": check_agent,
                "message": get_recipient_prompt('check', user_input),
                "max_turns": 1,
                "summary_method": "reflection_with_llm",
                "summary_args": {
                    "summary_prompt": get_summary_prompt("check")
                }
            },
            {
                "recipient": query_agent,
                "message": generatePrompting(user_input),
                "max_turns": 1,
                "summary_method": "reflection_with_llm",
                "summary_args": {
                    "summary_prompt": get_summary_prompt("query")
                }
            }
        ]
    )
    print(result[-1].summary)
    return result[-1].summary

return_menu_query_information("Can I have a large double cheeseburger combo meal")
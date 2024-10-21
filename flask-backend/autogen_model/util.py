from autogen_model.prompt import (
    ENTRYPOINT_AGENT_SYSTEM_MESSAGE,
    TRANSCRIPTION_SUMMARY_PROMPT,
    QUERY_AGENT_SYSTEM_MESSAGE,
    TRANSCRIPTION_SUMMARY_PROMPT,
    QUERY_AGENT_PROMPT,
    TRANSCRIPTION_SUMMARY_PROMPT,
    QUERY_SUMMARY_PROMPT,
    CHECK_AGENT_SYSTEM_MESSAGE,
    CHECK_AGENT_PROMPT,
    CHECK_SUMMARY_PROMPT,
    get_check_prompt
)

def get_system_message(task_name):
    if task_name == "entrypoint":
        return ENTRYPOINT_AGENT_SYSTEM_MESSAGE
    elif task_name == "transcription":
        return TRANSCRIPTION_SUMMARY_PROMPT
    elif task_name == "query":
        return QUERY_AGENT_SYSTEM_MESSAGE
    elif task_name == "check":
        return CHECK_AGENT_SYSTEM_MESSAGE

def get_recipient_prompt(task_name, user_input=None):
    if task_name == "transcription":
        return TRANSCRIPTION_SUMMARY_PROMPT
    elif task_name == "query":
        return QUERY_AGENT_PROMPT
    elif task_name == "check":
        return get_check_prompt(user_input)

def get_summary_prompt(task_name):
    if task_name == "transcription":
        return TRANSCRIPTION_SUMMARY_PROMPT
    elif task_name == "query":
        return QUERY_SUMMARY_PROMPT
    elif task_name == "check":
        return CHECK_SUMMARY_PROMPT
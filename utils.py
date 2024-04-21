from bson.objectid import ObjectId
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

def get_index_of_case(user_cases, case_id):
    """
    Find the index of a case with the specified case_id in a list of cases.

    Parameters:
        user_cases (list): A list of dictionaries, each representing a case.
        case_id (str): The string identifier of the case to find.

    Returns:
        int: The index of the case in the list, or None if not found.
    """
    for index, case in enumerate(user_cases):
        if case['_id'] == ObjectId(case_id):
            return index
    return None

def convert_mongodb_messages_to_langchain_format(messages):
    result = []
    for message in messages:
        if message["role"] == "system":
            result.append(SystemMessage(content=message["content"]))
        elif message["role"] == "human":
            result.append(HumanMessage(content=message["content"]))
        elif message["role"] == "ai":
            result.append(AIMessage(content=message["content"]))
    return result
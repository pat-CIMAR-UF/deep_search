# Import dependencies
from ragflow_sdk import RAGFlow  # client for the RAG service
from ragflow.rag_config import _load_ragflow_env

# Create a RAGFlow client
api_key, base_url = _load_ragflow_env()
ragflow_client = RAGFlow(api_key=api_key, base_url=base_url)


# 1. List chat assistants and their knowledge bases (so we know what data RAG can provide)
def get_assistant_list():
    # 1. Create the RAGFlow client
    # 2. List all chat assistants (page: int = 1, page_size: int = 30)
    chat_list = ragflow_client.list_chats()
    # 3. Collect each assistant's knowledge-base info
    count_chat_info = ""  # accumulated assistant info
    for chat in chat_list:
        dataset_names = []
        dataset_list = chat.datasets  # knowledge bases bound to this assistant
        if dataset_list and isinstance(dataset_list, list):
            # knowledge-base name
            for dataset in dataset_list:
                print(dataset)
                dataset_names.append(dataset['name'])  # collect dataset names for this assistant

        # Append this assistant's info + knowledge-base names
        # e.g. Legal Aid Assistant  xxxxxx  Associated knowledge bases: xx, xxx, xxx
        count_chat_info += f"assistant name:{chat.name}; description:{chat.description}; associated knowledge bases: {', '.join(dataset_names)} \n"
    # 4. Return the combined text for the model (so it knows which assistant to call)
    return count_chat_info


# 2. Ask an assistant a question (create session -> ask -> delete session)
def ask_question(chat_name, question):
    """
    Ask an assistant a question: 1. create a session 2. ask 3. close the session.
    :param chat_name: assistant name (get_assistant_list only exposes names to the LLM)
    :param question: the question to ask
    :return: the answer
    """
    """
                                                ---> dataset
       we (agent) ----》 session  --》 chat (assistant) ---> dataset
                                                ---> dataset
    """
    # 1. Create the RAGFlow client
    # 2. Look up the chat by name
    chats = ragflow_client.list_chats(name=chat_name)
    use_chat = chats[0]  # the assistant we will use
    # 3. Create a session on the chat
    session = use_chat.create_session(name="temp_session_ask")
    # 4. Ask through the session
    # The response is streamed
    response = session.ask(question=question, stream=True)
    # Collect the full answer
    result = ""
    # Each chunk of the stream is a part object
    for part in response:
        # The text lives on part.content
        print(part.content)
        result = part.content
    # 5. Close the session
    # chat -> delete -> session
    use_chat.delete_sessions(ids=[session.id])
    # 6. Return the result
    return result


if __name__ == '__main__':
    print(get_assistant_list())
    print(ask_question("法律援助助手", "What should I do if I have caused someone a disability?"))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

document_analysis_prompt = ChatPromptTemplate.from_template(
    """
    You are highly capable assistant that is trained to analyze and summarize the documents.
    Return ONLY valid JSON matching the schema mentioned below.

    {format_instructions}

    Analyze this document:
    {document_text}

    """
)


document_comparison_prompt = ChatPromptTemplate.from_template(
    """
    You are highly capable assistant that is trained to compare and summarize the documents.
    You have to perform the following tasks:

    1. Compare the content of two documents.
    2. Identify the differences between the two documents and note down the page number.
    3. The output which you provide must be page wise comparison content.
    4. If no changes found in any of the pages, return "NO CHANGE"


    Return ONLY valid JSON matching the schema mentioned below.

    {format_instructions}

    Analyze these document:
    {document_text_combined}

    """
)

contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", 
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
]) 

# Prompt for answering based on context
context_qa_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an assistant designed to answer questions using the provided context. Rely only on the retrieved "
        "information to form your response. If the answer is not found in the context, respond with 'I don't know.' "
        "Keep your answer concise and no longer than three sentences.\n\n{context}"
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

PROMPT_REGISTRY = {
    "document_analysis": document_analysis_prompt,
    "document_comparison": document_comparison_prompt,
    "contextualize_prompt": contextualize_prompt,
    "context_qa": context_qa_prompt,
}
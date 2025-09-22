from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder

document_analyzer_prompt = ChatPromptTemplate.from_template(
    """
    You are an extremly helpful AI assistant who excels in analyzing and summarizing the documents.
    Return the output only in valid specificied JSON format.

    {format_instructions}

    Analyze this document
    {document_text}    
    """
)

document_comparer_prompt = ChatPromptTemplate.from_template(
    """
    You are an extremly helpful AI assistant who excels in comparing documents.
    Return the output only in valid specificied JSON format.

    Format Instructions
    {format_instructions}

    Combined Douments
    {combined_documents}
  
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
    "document_analyzer_prompt": document_analyzer_prompt,
    "document_comparer_prompt": document_comparer_prompt,
    "contextualize_prompt": contextualize_prompt,
    "context_qa_prompt": context_qa_prompt
}
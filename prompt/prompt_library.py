from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    """
    You are highly capable assistant that is trained to analyze and summarize the documents.
    Return ONLY valid JSON matching the schema mentioned below.

    {format_instructions}

    Analyze this document:
    {document_text}

    """
)
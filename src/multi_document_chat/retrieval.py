import os
import sys
from operator import itemgetter
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import BaseMessage

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from models.models import PromptType
from prompts.prompt_library import PROMPT_REGISTRY


class ConversationalRAG:
    """
    Class for Conversational RAG for multi document chat.
    """
    def __init__(self, session_id:str, retriever=None):
        self.logger = CustomLogger().get_logger(__name__)
        self.session_id = session_id
        try:
            self.logger.info("Starting to initialise ConversationalRAG.")
            self.loader = ModelLoader()
            self.llm = self._load_llm()
            
            self.contextualize_prompt = PROMPT_REGISTRY.get(PromptType.CONTEXTUALIZE_QUESTION.value)
            self.qa_prompt = PROMPT_REGISTRY.get(PromptType.CONTEXT_QA.value)

            if not retriever:
                raise ValueError("Retriever cannot be null.")
            self.retriever = retriever

            self._build_lcel_chain()

            self.logger.info("ConversationalRAG has been initialized.")
        except Exception as e:
            self.logger.error("An error has occured while initialising ConversationalRAG.")
            raise DocumentPortalException(e, sys)

    def load_retriever_from_faiss(self, faiss_index_path:str):
        """
        Load retriever from faiss and return a retriever.
        """
        try:
            if not os.path.exists(faiss_index_path):
                raise FileNotFoundError(f"Index file not found at {faiss_index_path}")
            
            vector_store = FAISS.load_local(folder_path=faiss_index_path, embeddings=self.loader.load_embedding(), allow_dangerous_deserialization=True)
            retriever = vector_store.as_retriever(search_typ="similarity", search_kwargs={"k": 5})
            self.logger.info("Retriever has been loaded from faiss successfully.")
            return retriever
        except Exception as e:
            self.logger.info("An error has occured while loading retriever from faiss.", error_message=e)
            raise DocumentPortalException(e, sys)

    def invoke(self, user_input:str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """
        Invoke ConversationalRAG.

        Args:
            user_input (Optional[List[BaseMessage]]): User input.

        Returns:
            str: Answer.
        """
        try:
            if not input:
                raise ValueError("Input cannot be null.")

            chat_history = chat_history | []
            payload = {"input": user_input, "chat_history":chat_history }
            answer = self.chain.invoke(payload)
            
            if not answer:
                self.logger.warning("No answer generated from LLM.", session_id=self.session_id, user_input=input)
                return "No answer generated."
            
            self.logger.info("Invoked chain successfully.", session_id=self.session_id, user_input=input, answer=answer[:150])
            return answer

        except Exception as e:
            self.logger.info("An error has occured while invoking ConversationalRAG.", error_message=e)
            raise DocumentPortalException(e, sys)

    def _load_llm(self):
        try:
            self.logger.info("Loading llm...")
            llm = self.loader.load_llm()
            if not llm:
                raise ValueError("LLM cannot be null.")
            self.logger.info("LLM has been loaded successfully.")
            return llm

        except Exception as e:
            self.logger.info("An error has occured while loading llm.", error_message=e)
            raise DocumentPortalException(e, sys)

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    def _build_lcel_chain(self):
        try:
            # 1. Rewrite question using chat history.
            question_rewriter = (
                {
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2. Retrieve documents using retriever.
            retrieved_docs = question_rewriter | self.retriever | self._format_docs
            
            # 3. Feed context + question + chat history to qa prompt.
            self.chain = (
                {
                    "context": retrieved_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )

        except Exception as e:
            self.logger.info("An error has occured while building lcel chain.", error_message=e)
            raise DocumentPortalException(e, sys)
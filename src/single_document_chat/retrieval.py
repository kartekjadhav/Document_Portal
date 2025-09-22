import os
import sys
import streamlit as st
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from prompts.prompt_library import PROMPT_REGISTRY
from models.models import PromptType
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.vectorstores import FAISS



class ConversationalRAG:
    def __init__(self, session_id:str, retriever):
        self.logger = CustomLogger().get_logger(__name__)
        self.session_id = session_id
        self.retriever = retriever
        try:
            self.llm = self._llm_loader()

            self.contextualize_prompt = PROMPT_REGISTRY.get(PromptType.CONTEXTUALIZE_QUESTION)
            self.qa_prompt = PROMPT_REGISTRY.get(PromptType.CONTEXT_QA)

            self.history_aware_retriever = create_history_aware_retriever(self.llm, self.retriever, self.contextualize_prompt)
            self.qa_chain = create_stuff_documents_chain(llm=self.llm, prompt=self.qa_prompt)

            rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)

            self.chain = RunnableWithMessageHistory(
                rag_chain,
                self._get_session_history,
                input_messages_key="input",
                output_messages_key="answer",
                history_messages_key="chat_history"
            )

            self.logger.info("ConversationalRAG has been initialized.")

        except Exception as e:
            self.logger.error("An error has occured while initialising ConversationalRAG.", error_message=e)
            raise DocumentPortalException(e, sys)
        
    
    def _get_session_history(self, session_id:str) -> BaseChatMessageHistory:
        if "store" not in st.session_state:
            st.session_state.store = {}
        
        if session_id not in st.session_state.store:
            st.session_state.store[session_id] = ChatMessageHistory()
        
        return st.session_state.store[session_id]

    def _llm_loader(self):
        try:
            llm = ModelLoader().load_llm()
            self.logger.info("LLM model loaded successfully", llm_model = llm)
            return llm
        except Exception as e:
            self.logger.error("An error has occured while initialising _llm_loader.", error_message=e)
            raise DocumentPortalException(e, sys)
        
    def invoke(self, user_question:str):
        try:
            response = self.chain.invoke(
                {"input": user_question},
                config={"configurable": {"session_id": self.session_id}}    
            )

            answer = response.get("answer", "No response")

            if answer=="No response":
                self.logger.warning("No answer generated from LLM.", session_id=self.session_id, user_question=user_question)
            
            self.logger.info("Chain invoked successfully.", session_id=self.session_id, user_question=user_question, answer=answer)

            return answer

        except Exception as e:
            self.logger.error("An error has occured while initialising invoke.", error_message=e)
            raise DocumentPortalException(e, sys)
        
    def load_retriever_from_faiss(self, index_path:str):
        try:
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index file not found at {index_path}")
            
            vectore_store = FAISS.load_local(folder_path=index_path, embeddings=ModelLoader().load_embedding(), allow_dangerous_deserialization=True)
            retriever = vectore_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            return retriever

        except Exception as e:
            self.logger.error("An error has occured while initialising _load_retriever_from_faiss.", error_message=e)
            raise DocumentPortalException(e, sys)
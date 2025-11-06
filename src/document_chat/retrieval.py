from operator import itemgetter
from typing import List, Optional, Any, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompts.prompt_library import PROMPT_REGISTRY
from models.models import PromptType


class ConversationalRAG:
    """
    Class for Conversational RAG for multi document chat.

    Usage:
        rag = ConversationalRAG(session_id='abc, retriver)
        retriver = rag.load_retriever_from_faiss(faiss_index='faiss_index)
        anser = rag.invoke('What is .... ?', chat_history)
    """
    def __init__(self, session_id:Optional[str], retriever=None):
        try:
            self.logger = CustomLogger().get_logger(__name__)
            self.logger.info("Starting to initialise ConversationalRAG.")

            self.session_id = session_id

            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.retriever = retriever

            if not retriever:
                raise ValueError("Retriever is not provided.")
            
            if retriever is not None:
                self._buld_lcel_chain()

            self.logger.info("ConversationalRAG has been initialized.", session_id=self.session_id)
        except Exception as e:
            self.logger.error("An error has occured while initialising ConversationalRAG.")
            raise DocumentPortalException(f"An error has occured while initialising ConversationalRAG. {str(e)}", e) from e
        
    def load_retriever_from_faiss(
        self,
        index_path:str,
        k:int=5,
        index_name:str='index',
        search_type:str="similarity",
        search_kwargs:Optional[Dict[str, Any]]={'k': 5}
    ):
        """
        Load FAISS vectorstore from disk and build retriever + LCEL chain.
        """
        try:
            self.logger.info("Loading retriever from faiss.", index_path=index_path, k=k, index_name=index_name, search_type=search_type, search_kwargs=search_kwargs)

            vs = FAISS.load_local(
                folder_path=index_name,
                embeddings=self.loader.load_embedding(),
                allow_dangerous_deserialization=True,
                index_name=index_name
            )

            self.retriever = vs.as_retriever(search_type, search_kwargs)
            self._build_lcel_chain()

            self.logger.info("Loaded retriever from faiss.", index_path=index_path, k=k, index_name=index_name, search_type=search_type, search_kwargs=search_kwargs)
        
            return self.retriever
        except Exception as e:
            self.logger.error("An error has occured while loading retriever from faiss.")
            raise DocumentPortalException(f"An error has occured while loading retriever from faiss. {str(e)}", e) from e

    @staticmethod
    def _format_docs(self, docs) -> str:
        return "\n\n".join([getattr(doc, 'page_content', str(doc)) for doc in docs])

    def invoke(self, user_input:str, chat_history:Optional[List[BaseMessage]]):
        try:
            if self.chain is None:
                raise DocumentPortalException("LCEL chain is not built yet. First build the chain by calling _build_lcel_chain().")

            chat_history = chat_history or []

            response = self.chain.invoke({
                'input': user_input,
                'chat_history': chat_history
            })

            self.logger.info("Answer has been generated.", session_id=self.session_id, user_input=user_input,response=response[:20])

            return response if response else 'Response not generated.'
        except Exception as e:
            pass

    def _build_lcel_chain(self):
        try:
            self.logger.info("Building LCEL chain.")

            if self.retriever is None:
                raise DocumentPortalException("No retriever set before building chain.")
            
            # 1. Rewrite the question with chat history
            question_rewriter = (
                {
                    'input': itemgetter('input'),
                    'chat_history': itemgetter('chat_history')
                }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2. Retrieve docs for rewritten question
            retrived_docs = (
                question_rewriter
                | self.retriever
                | self._format_docs
            )

            # 3. Answer using retrieved content + original question + chat history
            self.chain = (
                {   'context': retrived_docs,
                    'input': itemgetter('input'),
                    'chat_history': itemgetter('chat_history')
                } 
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            ) 

            self.logger.info("LCEL chain has been built.")
        except Exception as e:
            self.logger.error("An error has occured while building LCEL chain.")
            raise DocumentPortalException(f"An error has occured while building LCEL chain. {str(e)}", e) from e

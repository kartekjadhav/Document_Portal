import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from utils.config import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception_archive import DocumentPortalException



class ModelLoader:
    """
    Loads the models from the configuration file.
    """
    def __init__(self):
        try:
            self.logger = CustomLogger().get_logger(__name__)
            load_dotenv()
            self._validate_env()
            self.config = load_config()
            self.logger.info("Validated environment variables and loaded config for ModelLoader.")
        except Exception as e:
            self.logger.error("An error has occured while initialising ModelLoader.")
            raise DocumentPortalException(e, sys)

    def _validate_env(self):
        """
        Validates the environment variables.
        """
        try:
            required_keys = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
            self.api_keys = {key: os.getenv(key) for key in required_keys}
            missing_leys = [key for key, value in self.api_keys.items() if not value]
        
            if missing_leys:
                self.logger.error(f"Missing environment variables: {', '.join(missing_leys)}")
                raise DocumentPortalException(f"Missing environment variables: {', '.join(missing_leys)}", sys)
            
            self.logger.info("Environment variables have been validated successfully and all required keys are present.")

        except Exception as e:
            self.logger.error("An error has occured while validating environment variables.")
            raise DocumentPortalException(e, sys)

    def load_llm(self):
        """
        Loads the LLM model from the configuration file.
        """

        try:
            self.logger.info("Starting LLM loading configuration.")
            llm_block = self.config["llm"]

            provider_key = os.getenv("LLM_PROVIDER", "groq")

            if provider_key not in llm_block:
                self.logger.error(f"Invalid LLM provider: {provider_key}")
                raise DocumentPortalException(f"Invalid LLM provider: {provider_key}", sys)

            llm_config = llm_block[provider_key]
            provider = llm_config.get("provider", "groq").lower()
            model = llm_config.get("model")
            temperature = llm_config.get("temperature", 0.1)
            max_token = llm_config.get("max_tokens", 2048)

            self.logger.info("LLM configuration loaded successfully.", provider=provider, model=model, temperature=temperature, max_token=max_token)

            if provider == "google":
                self.logger.info("Loading GOOGLE LLM...")
                llm = ChatGoogleGenerativeAI(model=model, temperature=temperature, max_tokens=max_token)
                self.logger.info("Google LLM model loaded successfully", llm_model = llm)
                return llm
            elif provider == "groq":
                self.logger.info("Loading GROQ LLM...")
                llm = ChatGroq(model=model, temperature=temperature, max_tokens=max_token)
                self.logger.info("Groq LLM model loaded successfully", llm_model = llm)
                return llm
            else:
                self.logger.info("Loading default LLM...")
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=2048)
                self.logger.info("Openai LLM model loaded successfully", llm_model = llm)
                return llm

        except Exception as e:
            self.logger.error("An error has occured while getting LLM model.")
            raise DocumentPortalException(e, sys)

    def load_embedding(self):
        """
        Loads the embedding model from the configuration file.
        """
        try:
            self.logger.info("Loading embedding model...")
            model = self.config["embedding"]["model"]
            embbeding = GoogleGenerativeAIEmbeddings(model=model)
            
            self.logger.info("Embeddinng mode loaded successfully.", embedding=embbeding)

            return embbeding
        except Exception as e:
            self.logger.error("An error has occured while getting embedding model.")
            raise DocumentPortalException(e, sys)
        


if __name__ == "__main__":
    model_loader = ModelLoader()
    llm = model_loader.load_llm()
    print("llm", llm)
    embedding = model_loader.load_embedding()
    print("embedding", embedding)

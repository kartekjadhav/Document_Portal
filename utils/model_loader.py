import os
import sys
from dotenv import load_dotenv
from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
log = CustomLogger().get_logger(__name__)

class ModelLoader:

    """
    A utility class for loading models and configurations for the Document Portal application.
    """

    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configuration loaded successfully.", config_keys=list(self.config.keys()))

    def _validate_env(self):
        """
        Validates that all required environment variables are set.
        Ensure API keys are set in the .env file.
        """
        required_vars = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.api_keys = {key:os.getenv(key) for key in required_vars}
        missing_vars = [k for k, v in self.api_keys.items() if not v]
        if missing_vars:
            log.error(f"Missing required environment variables: ", missing_vars=missing_vars)
            raise DocumentPortalException(f"Missing required environment variables", sys)
        log.info("Enviroment variable validate", available_keys=list(self.api_keys.keys()))

    def load_llm(self):
        """
        Loads the LLM model based on the configuration.
        """

        llm_block = self.config['llm']
        log.info("Loading LLM model...")
        provider_key = os.getenv("LLM_PROVIDER", "groq")
        if provider_key not in llm_block:
            log.error(f"Provider key '{provider_key}' not found in LLM configuration.")
            raise ValueError(f"Provider key '{provider_key}' not found in LLM configuration", sys)

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider", "groq").lower()
        temperature = llm_config.get("temperature", 0.1)
        max_output_tokens = llm_config.get("max_output_tokens", 2048)
        model_name = llm_config.get("model_name")

        log.info("LLM configuration loaded", provider=provider, temperature=temperature, max_output_tokens=max_output_tokens, model_name=model_name)

        if provider == 'google':
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_output_tokens,
                api_key=self.api_keys.get("GOOGLE_API_KEY", None)
            )

        elif provider_key == 'groq':
            return ChatGroq(
                model=model_name,
                temperature=temperature,
                max_tokens=max_output_tokens,
                api_key=self.api_keys.get("GROQ_API_KEY", None)
            )

        elif provider == 'openai':
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_output_tokens,
                api_key=self.api_keys.get("OPENAI_API_KEY", None)
            )
        
        else:
            log.error(f"Unsupported provider", provider=provider)
            raise ValueError(f"Unsupported Provider: {provider}", sys)

    def load_embbeddings(self):
        """
        Loads the embeddings model based on the configuration.
        """

        try:
            log.info("Loading embeddings model...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Failed to load embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)

if __name__ == "__main__":
    model_loader = ModelLoader()

    #Test embedding model
    embeddings = model_loader.load_embbeddings()
    print(f"Embedding Model Loaded: {embeddings}")
    
    # Test the Embedder
    result = embeddings.embed_query("Hello, how are you?")
    print(result)

    # Test LLM mode loading
    llm = model_loader.load_llm()
    print(f"LLM Model Loaded: {llm}")

    # Invoke LLM model
    result = llm.invoke("Hello, how are you?") 
    print(f"LLM result: {result.content}")

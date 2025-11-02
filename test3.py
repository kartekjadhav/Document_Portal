# Test code for document analyzer

from pathlib import Path
from src.document_analyser.document_analyser import DocumetAnalyzer
from src.document_ingestion.data_ingestion import DocHandler


class DummmyFile:
    def __init__(self, file_path:str):
        self.name = Path(file_path).name
        self.file_path = file_path  
    def get_buffer(self):
        return open(self.file_path, "rb").read()
    

def analyze():
    file_path = r"C:\Users\hp\OneDrive\Documents\Kartek\LLMOPS\Document_Portal\data\NIPS-2017-attention-is-all-you-need-Paper.pdf"
    upload_file = DummmyFile(file_path=file_path)
    
    # 1. Ingestion
    docHandler = DocHandler()
    save_path = docHandler.save_pdf(uploaded_file=upload_file)
    text_docs = docHandler.read_pdf(save_path=save_path)


    # 2. Analyze
    docAnalyzer = DocumetAnalyzer()
    response:dict = docAnalyzer.analyze_document(docs=text_docs)
    
    for k, v in response.items():
        print(f"\n{k}: {v}\n")


if __name__ == "__main__":
    analyze()
import sys
import traceback

class DocumentPortalException(Exception):
    def __init__(self, error_message, error_details:sys):
        _, _, exc_tb = error_details.exc_info()
        self.filename = exc_tb.tb_frame.f_code.co_filename
        self.line_number = exc_tb.tb_lineno
        self.error_message = str(error_message)
        self.traceback_str = "".join(traceback.format_exception(*error_details.exc_info()))
    
    def __str__(self):
        return f"""
            Error occured in Filename: {self.filename} at Line Number: {self.line_number}
            Error message: {self.error_message}
            Traceback:
                {self.traceback_str}
        """
    
if __name__=="__main__":
    from logger.custom_logger import CustomLogger
    logger = CustomLogger().get_logger(__file__)
    try:
        a = 1 / 0 # Intentional exception
    except Exception as e:
        logger.error("An error has been occured.", file_name="xyz.pdf", user_id=123, user="kj")
        raise DocumentPortalException(error_message=e,error_details=sys)
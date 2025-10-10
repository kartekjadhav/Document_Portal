import sys
import traceback
from typing import Optional, cast


class DocumentPortalException(Exception):
    def __init__(self, error_message:str, error_details:Optional[object] = None):
        # Normalize the message
        normalized = str(error_message)

        exc_type = exc_value = exc_traceback = None

        if error_details is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):
                exc_detail_object = cast(sys, error_details)
                exc_type, exc_value, exc_traceback = exc_detail_object.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_traceback = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Find the last tb
        last_tb = exc_traceback
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.filename = last_tb.tb_frame.f_code.co_filename if last_tb else '<unknown>'
        self.line_no = last_tb.tb_lineno if last_tb else -1
        self.error_message = normalized

        # Format the traceback
        if exc_type and exc_traceback:
            self.traceback_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        else:
            self.traceback_msg = ""

        super().__init__(self.__str__())

    def __str__(self):
        # Compact, logger-friendly message (no leading spaces)
        base = f"Error in [{self.filename}] at line [{self.line_no}] | Message: {self.error_message}"
        if self.traceback_msg:
            return f"{base}\nTraceback:\n{self.traceback_msg}"
        return base

    def __repr__(self):
        return f"DocumentPortalException(file={self.filename!r}, line={self.line_no}, message={self.error_message!r})"



if __name__ == '__main__':
    # Demo 1
    try:
        a = 1/0
        print("Error came or not?")
    except Exception as e:
        raise DocumentPortalException(e, sys)

    # # Demo 2
    # try:
    #     a = int("abc")
    #     print("Error came or not?")
    # except Exception as e:
    #     raise DocumentPortalException(e, sys) 




# What Does super().__init__() Do?
# pythonsuper().__init__(self.__str__())
# Breakdown:

# super(): Refers to the parent class (Exception)
# .__init__(): Calls the parent's constructor
# self.__str__(): Passes our formatted error message to the parent


# Why Do This?
# Without super().__init__():
# pythontry:
#     raise DocumentPortalException("Test error")
# except DocumentPortalException as e:
#     print(str(e))  # Works - uses our __str__() method
#     print(e.args)  # Returns: ()  ← EMPTY!
# With super().__init__(self.__str__()):
# pythontry:
#     raise DocumentPortalException("Test error")
# except DocumentPortalException as e:
#     print(str(e))  # Works - uses our __str__() method
#     print(e.args)  # Returns: ('Error in [file.py] at line [10] | Message: Test error',)


# Without !r:
# pythonfile_name = "helper.py"
# print(f"file={file_name}")
# # Output: file=helper.py
# With !r:
# pythonfile_name = "helper.py"
# print(f"file={file_name!r}")
# # Output: file='helper.py'  ← Notice the quotes!











# Why from e in Exception Raising?
# Quick Answer
# from e preserves the original exception while raising a new one. It creates a chain showing "this happened BECAUSE of that."
# 
# The Difference
# Without from e:
# pythontry:
#     result = 1 / 0
# except Exception as e:
#     raise DocumentPortalException("Math operation failed")
# Output:
# DocumentPortalException: Error in [main.py] at line [5] | Message: Math operation failed
# ❌ Lost info: You don't see the original ZeroDivisionError!

# With from e:
# pythontry:
#     result = 1 / 0
# except Exception as e:
#     raise DocumentPortalException("Math operation failed", e) from e
# Output:
# Traceback (most recent call last):
#   File "main.py", line 2, in <module>
#     result = 1 / 0
# ZeroDivisionError: division by zero

# The above exception was the direct cause of the following exception:

# Traceback (most recent call last):
#   File "main.py", line 4, in <module>
#     raise DocumentPortalException("Math operation failed", e) from e
# DocumentPortalException: Error in [main.py] at line [2] | Message: Math operation failed
# ✅ Shows both: Original error AND your custom error!
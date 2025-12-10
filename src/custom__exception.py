import traceback
import sys

class CustomException(Exception):
    
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message, error_detail)

    @staticmethod
    def get_detailed_error_message(error_message, error_detail:sys):
        """
        Build a detailed error message with file name and line number.
        Uses current exception info from sys.exc_info().
        """
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_tb is not None:
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
            return (
                f"Error occured in {file_name}, line number {line_number}: "
                f"{error_message}. Original error: {repr(error_detail)}"
            )  
        else:
            # Fallback if no traceback is available
            return f"{error_message}. Original error: {repr(error_detail)}"
    
    def __str__(self):
        return self.error_message
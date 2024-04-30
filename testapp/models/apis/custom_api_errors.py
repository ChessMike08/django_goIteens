class CustomAPIError(Exception):
    """
    Тип общий класс наших ошибок для АПИ.
    Для вывода ошибки:
    ```py
    except CustomAPIError as e:
    print(f"Error: {e}")
    ```
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class BadRequestAPIError(CustomAPIError):
    """Когда в АПИ нет такого кода-языка"""

    def __init__(self):
        super().__init__("Status 400. Bad Request. Try another param.")


class UnauthorizedAPIError(CustomAPIError):
    """Когда действие АПИ-ключа закончилось"""

    def __init__(self):
        super().__init__(
            "Status 401. Unauthorized. Please, report the problem with the API key-password to the main administrator."
        )


class ForbiddenAPIError(CustomAPIError):
    """Для запрещенного запроса"""

    def __init__(self):
        super().__init__("Status 403. Forbidden. Try another request.")


class NonTypicalStatusAPIError(CustomAPIError):
    """Не типичный статус (не прописан в дукоментации)"""

    def __init__(self, status_code):
        super().__init__(
            f"Status {status_code}. Status: The API has an atypical status. Please report an error with atypical status of response API to the main administrator (with code)."
        )


class ParamStrNoneOrEmptyError(CustomAPIError):
    """Когда ничего не передали в функцию или же строка пустая"""

    def __init__(self):
        super().__init__(
            "Parameter is not passed to the data retrieval function or empty."
        )


class HeadersNumberError(CustomAPIError):
    """Когда в настройках нет переменной с нужным числом"""

    def __init__(self, number):
        super().__init__(
            f"There is no setting with this number ({number}). Try another number."
        )

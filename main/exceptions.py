from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler

exception_message = {
    "field_verification_fail": "字段验证失败。",
    "not_active": "还没有验证邮箱。",
    "email_send_fail": "邮件发送失败",

}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = dict()
        response.data = {
            "errors_info": {}
        }
        if not isinstance(exc, ValidationError):
            response.data.get("errors_info")["message"] \
                = exception_message.get(exc.get_codes, 'No message.')
            response.data["status_code"] = exc.get_codes()
            response.data.get("errors_info")["detail"] = exc.detail
        else:
            response.data["status_code"] = "field_verification_fail"
            response.data["errors_info"] = exc.get_full_details()
            response.data["errors_info"]["message"] \
                = exception_message.get("field_verification_fail", "No message.")

    return response


class EmailSendFailException(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "Fail to send the verification email."
    default_code = "email_send_fail"

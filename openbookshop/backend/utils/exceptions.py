from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """自定义异常处理，统一响应格式"""
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data

        # Extract message from various error formats
        if isinstance(detail, dict):
            if "detail" in detail:
                message = str(detail["detail"])
            else:
                messages = []
                for field, errors in detail.items():
                    if isinstance(errors, list):
                        messages.append(f"{field}: {'; '.join(str(e) for e in errors)}")
                    else:
                        messages.append(f"{field}: {errors}")
                message = "; ".join(messages)
        elif isinstance(detail, list):
            message = "; ".join(str(item) for item in detail)
        else:
            message = str(detail)

        response.data = {
            "code": response.status_code,
            "message": message,
            "data": None,
        }

    return response

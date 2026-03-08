from rest_framework.response import Response


def success_response(data=None, message="success", code=200):
    """标准成功响应"""
    return Response({
        'code': code,
        'message': message,
        'data': data,
    }, status=code)


def error_response(message="error", code=400, data=None):
    """标准错误响应"""
    return Response({
        'code': code,
        'message': message,
        'data': data,
    }, status=code)

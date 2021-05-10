"""
@time: 2020/12/22 下午3:58
"""
import json

from main.utils import PermissionAPIView


def health(request):
    return request.response(response_code=200)


class Demo(PermissionAPIView):
    authentication_classes = []

    def get(self, request):
        return request.response.success()

    def post(self, request):
        print('{sp} Get Request {sp}'.format(sp='#' * 13))
        print('{sp} data {sp}'.format(sp='-' * 15))
        print(json.dumps(request.data, indent=2))

        if 'request' in request.data:
            uid = request.data.get('request').get('uid')
            apiVersion = request.data.get('apiVersion')
        else:
            uid = None
            apiVersion = None
        response = {"apiVersion": apiVersion, "kind": 'AdmissionReview', 'response': {"uid": uid, "allowed": True}}
        print('{sp} response {sp}'.format(sp='-' * 13))
        print(json.dumps(response, indent=2))
        print('{sp} Request End {sp}'.format(sp='#' * 13))
        return request.response.success(**response)

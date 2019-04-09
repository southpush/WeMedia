from rest_framework.response import Response as OldResponse
from rest_framework.serializers import Serializer
from django.utils import six


class Response(OldResponse):
    def __init__(self, data=dict(), status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None,
                 status_code=0):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.

        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {
            "status_code": status_code,
            "data": data
        }
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value


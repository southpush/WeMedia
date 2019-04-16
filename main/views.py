from rest_framework import generics, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from main.models import Posts
from main.response import Response
from user.auth import TokenAuthentication, PublishPostsPermission


class PostsList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication, IsAuthenticatedOrReadOnly)
    permission_classes = (PublishPostsPermission, DjangoModelPermissionsOrAnonReadOnly)

    def get_queryset(self):
        user = self.request.user
        return Posts.objects.get(author=user.profile)


class TestView(APIView):
    def get(self, request):
        print(request)
        return Response('ooopok', status=status.HTTP_200_OK)


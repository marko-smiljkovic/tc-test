from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from user import models, serializers
from tctest import exceptions


class UserSignupResource(APIView):
    """
    Resource used for user sign up
    """

    def post(self, request):
        # TODO change validation to use marshmallow for example
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        user = models.TCTestUser.register(email, password)
        user.save()

        return Response({'message': 'User successfully registered'})


class PostResource(APIView):
    """
    Resource used for adding/getting posts
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        text = request.data.get("text", None)
        post = models.Post(text=text, user=request.user)
        post.save()

        return Response(serializers.PostSerializer(post).data)

    def get(self, request):
        post_id = request.data.get("post_id", None)
        user_id = request.data.get("user_id", None)
        if post_id is not None:
            post = models.Post.objects.get(id=post_id)
            return Response(serializers.PostSerializer(post).data)
        if user_id is not None:
            posts = models.Post.get_user_posts_by_user_id(user_id)
            return Response(serializers.PostSerializer(posts, many=True).data)
        raise exceptions.MissingParameters


class LikeResource(APIView):
    """
    Resource for managing likes
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        post_id = request.data.get("post_id", None)
        like_value = request.data.get("like_value", True)
        post = models.Post.objects.get(id=post_id)
        if not post:
            raise exceptions.BadParameters
        post.like_or_unlike_post(request.user, like_value)
        return Response(serializers.PostSerializer(post).data)

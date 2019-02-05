from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    user = UserSerializer()
    like_count = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.postlike_set.count()

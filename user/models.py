import re
import json
import clearbit

from django.db import models
from django.contrib.auth.models import User
from tctest.utils.hunterio import HunterIO
from django.conf import settings

from tctest import exceptions


class TCTestUser(User):
    """
    TCTest has only one type of user, and that is this one :D
    """
    # TODO also this extending of user makes one unnecessary join, should rather extend base user or whatever ...
    # TODO would use JSON field, but that would make me require the use of mysql or postgres,
    # and its corresponding django module
    # TODO possibly create custom field that will do json.loads/dumps when reading/inserting for fun :D
    extensive_data = models.TextField(default=None, null=True)

    @classmethod
    def register(cls, email, password):
        """
        Method used for registering TCTest users. It checks for password strength, and if email provided passes
        hunterio check. Also it should get more data from https://clearbit.com/enrichment when its fixed
        :param email: email of the user
        :param password: password of the user
        :return: instantiated user object, with email and pass
        :rtype: TCTestUser
        """
        # Checking pass strength
        if not _check_pass_strength(password):
            raise exceptions.PasswordNotStrongEnough

        # Checking email validity on hunterio
        hunterio_client = HunterIO(
            settings.HUNTERIO_API_KEY,
            settings.HUNTERIO_API_URL,
        )
        # Comment this if hunterio key fails
        if hunterio_client.check_email(email) is not True:
            raise exceptions.InvalidEmailException

        # Creating user
        new_user, created = cls.objects.get_or_create(email=email, username=email)
        if not created:
            raise exceptions.UserAlreadyExists
        new_user.set_password(password)

        # Getting more data if available from clearbit
        clearbit.key = settings.CLEARBIT_API_KEY
        # Comment the enrichment and uncomment the empty dict to make it run faster if doing mass register through bot
        # lookup = {}
        lookup = clearbit.Enrichment.find(email=email, stream=True)
        if "person" in lookup and "name" in lookup["person"]:
            new_user.first_name = lookup["person"]["name"].get("givenName", None)
            new_user.last_name = lookup["person"]["name"].get("familyName", None)
        new_user.extensive_data = json.dumps(lookup)

        return new_user


def _check_pass_strength(password):
    """
    Function to check password strength
    :return: true if password is at least 8 char long, has at least 1 upper, lower and digit, else false
    :rtype: bool
    """
    length_regex = re.compile(r'.{8,}')
    uppercase_regex = re.compile(r'[A-Z]')
    lowercase_regex = re.compile(r'[a-z]')
    digit_regex = re.compile(r'[0-9]')

    return (length_regex.search(password) is not None
            and uppercase_regex.search(password) is not None
            and lowercase_regex.search(password) is not None
            and digit_regex.search(password) is not None)


class Post(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    text = models.TextField(null=False)

    @classmethod
    def get_user_posts(cls, user):
        """
        Returns all posts for a user
        :param user: user whose posts we want to get
        :return: list of posts
        :rtype: [Post]
        """
        return cls.objects.filter(user=user).all()

    @classmethod
    def get_user_posts_by_user_id(cls, user_id):
        """
        Returns all posts for a user
        :param user_id: user whose posts we want to get
        :return: list of posts
        :rtype: [Post]
        """
        return cls.objects.filter(user_id=user_id).all()

    def like_or_unlike_post(self, like_user, like_value=True):
        """
        Likes or unlikes current post. Raises error if user tries to like its own post.
        Makes sure that user can like same post only once.
        :param like_user: user that likes the post
        :param like_value: by default True, meaning by default it likes a post, if specified can unlike it
        :return: post like object
        :rtype: PostLike
        """
        if like_user == self.user:
            raise exceptions.CantLikeOwnPost
        post_like, created = PostLike.objects.get_or_create(post=self, user=like_user)
        post_like.is_liked = like_value
        post_like.save()
        return post_like

    @property
    def like_count(self):
        return PostLike.objects.filter(post=self, is_liked=True).count()


class PostLike(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)

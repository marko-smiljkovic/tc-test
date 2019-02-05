import json
import random
import string
from test_bot.api_caller import TCTestApiCaller, BaconIpsumApiCaller


class TheBot:

    config = None
    api_caller = None
    bacon_ipsum = None
    users = list()

    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)
        if self.config is None:
            print("Missing config!")
            raise Exception("Error, missing config")
        self.api_caller = TCTestApiCaller(self.config["api_server_url"])
        self.bacon_ipsum = BaconIpsumApiCaller()

    @staticmethod
    def _generate_email_with_salt(email_name, email_domain):
        """
        This is used to create somewhat random email, well its the same email as far as hunterio is concerned,
        but for tctest it will make a difference :D
        :param email_name:
        :param email_domain:
        :return:
        """
        salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return "{email_name}+{salt}{email_domain}".format(
            email_name=email_name,
            salt=salt,
            email_domain=email_domain,
        )

    def _register_user(self, email_name, email_domain, password):
        """
        Registers user with given data. In a case where user with random email already exists,
        creates again until successful
        :param email_name:
        :param email_domain:
        :param password:
        :return:
        """
        email = self._generate_email_with_salt(email_name, email_domain)
        response = self.api_caller.register_user(email, password)
        while response.status_code == 400 and response.json().get('detail') == 'User already exists':
            email = self._generate_email_with_salt(email_name, email_domain)
            response = self.api_caller.register_user(email, password)
        if response.status_code != 200:
            raise Exception("Something went wrong, {}: {}, panic!!!".format(response.status_code, response.json()))
        user = response.json()
        token_pair = self.api_caller.get_jwt_token_pair(email, password)
        print("Created user {}".format(email))
        return {
            "id": user["id"],
            "email": email,
            "password": password,
            "refresh_token": token_pair["refresh"],
            "access_token": token_pair["access"]
        }

    def _create_posts_for_user(self, user, max_posts_per_user):
        """
        Creates random number of posts for user up to max_posts_per_user
        :param user:
        :param max_posts_per_user:
        :return:
        """
        number_of_posts_to_create = random.randint(1, max_posts_per_user)
        for i in range(number_of_posts_to_create):
            # TODO Take care of expired access token.
            # It shouldn't really happen in this bot with not too big number of users to create, but its a possibility.
            # In that case, should try to refresh the token.
            post = self.api_caller.create_post(self.bacon_ipsum.get_bacon_ipsum(), user["access_token"])
            print("Post created: {}".format(post))

    def _refresh_users_posts(self):
        """
        Gets fresh posts, well basically refreshes likes counts,
        didn't wanna keep track of that in the bot, seemed like a bad idea
        :return:
        """
        for user in self.users:
            user["posts"] = self.api_caller.get_user_posts(user["id"], user["access_token"])
            user["number_of_posts"] = len(user["posts"])

    def _get_random_post_to_like(self, user_id):
        """
        The 'fun' method, getting somewhat random post, as it follows some rules -
        user can only like random posts from users who have at least one post with 0 likes
        if there is no posts with 0 likes, bot stops
        users cannot like their own posts
        posts can be liked multiple times, but one user can like a certain post only once
        :return: post id or None if its time to stop the bot !!!!
        """
        helper_list = list()
        user_to_pop = None
        for user in self.users:
            # Marking the user that is going to do the like action for later removal. Not removing now from list since
            # hes needed to check if all posts are already liked
            if user["id"] == user_id:
                user_to_pop = user
            for post in user["posts"]:
                # If theres a post with 0 likes, adds user to the pool
                if post["like_count"] == 0:
                    helper_list.append(user)
                    break

        # If there is no one in the list, means theres no post with 0 likes
        if len(helper_list) == 0:
            return None

        # Removing user that is going to like from the list, so he doesnt like his own post
        # (even though tctest wouldnt let that happen anyway)
        helper_list = [user for user in helper_list if user["id"] != user_to_pop["id"]]

        # Shuffling the list and posts, so i get the random post to like
        random.shuffle(helper_list)
        random.shuffle(helper_list[0]["posts"])

        # TODO now theres the thing with user should not like the same post twice. Skipping this for now,
        # since its a bother to think about what to do if actually
        # the number of likes the user should do exceeds number of posts that exist.
        # Would otherwise just keep track of what was already liked
        # P.S. tctest backend has no issues with user liking the same post twice, its just that nothing will happen

        return helper_list[0]["posts"][0]

    def do_the_test(self):
        """
        Main method that will do all the work
        :return:
        """
        number_of_users = self.config.get("number_of_users", 5)
        max_posts_per_user = self.config.get("max_posts_per_user", 5)
        max_likes_per_user = self.config.get("max_likes_per_user", 5)
        email_name = self.config.get("email_name", "churava13")
        email_domain = self.config.get("email_domain", "@gmail.com")
        # TODO maybe create random password if theres nothing else to do
        password = self.config.get("password", "Qwer4321!")

        for i in range(number_of_users):
            self.users.append(self._register_user(email_name, email_domain, password))

        for user in self.users:
            self._create_posts_for_user(user, max_posts_per_user)

        self._refresh_users_posts()

        users_ordered_by_posts_count = sorted(self.users, key=lambda k: k['number_of_posts'], reverse=True)

        for sorted_user in users_ordered_by_posts_count:
            for i in range(max_likes_per_user):
                post_to_like = self._get_random_post_to_like(sorted_user["id"])
                if post_to_like is None:
                    print("No post with 0 likes, time to end the thebot")
                    exit("ended")
                print("{} like {}".format(sorted_user["id"], post_to_like["id"]))
                self.api_caller.like_post(post_to_like["id"], sorted_user["access_token"])
                self._refresh_users_posts()

        print("All done, works like a charm!")


the_bot = TheBot("bot_config.json")
the_bot.do_the_test()


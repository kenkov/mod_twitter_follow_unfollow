#! /usr/bin/env python
# coding:utf-8


from mod import Mod
from datetime import datetime
import TwitterAPI
from logging import getLogger


class ModTwitterFollowUnfollow(Mod):
    def __init__(
        self,
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_secret,
        logger=None
    ):
        self.logger = logger or getLogger(__file__)

        # initialize superclass
        Mod.__init__(self, self.logger)

        self.basetime = datetime.now()
        self.api = TwitterAPI.TwitterAPI(
            consumer_key,
            consumer_secret,
            oauth_token,
            oauth_secret
        )

    def get_friends(self):
        return [item for item in self.api.request('friends/ids')]

    def get_followers(self):
        return [item for item in self.api.request('followers/ids')]

    def get_screen_name(self, user_id: int):
            return list(self.api.request(
                "users/show", {"user_id": user_id}
            ))[0]["screen_name"]

    def can_utter(
        self,
        message: dict,
        master: dict
    ):
        now = datetime.now()
        if now.hour < self.basetime.hour:

            friends = self.get_friends()
            followers = self.get_followers()
            self.logger.info(
                "friends: {}, followers: {}".format(
                    len(friends), len(followers)
                )
            )

            for user_id in set(friends) - set(followers):
                screen_name = self.get_screen_name(user_id)
                self.logger.info("trying to unfollow {}".format(screen_name))

                r = self.api.request(
                    "friendships/destroy",
                    {"user_id": user_id}
                )
                if r.status_code == 200:
                    self.logger.info("unfollow {}".format(screen_name))
                else:
                    self.logger.info(
                        "failed to unfollow {}".format(screen_name)
                    )

            for user_id in set(followers) - set(friends):
                screen_name = self.get_screen_name(user_id)
                self.logger.info("trying to follow {}".format(screen_name))

                r = self.api.request(
                    "friendships/create",
                    {"user_id": user_id}
                )
                if r.status_code == 200:
                    self.logger.info("follow {}".format(screen_name))
                else:
                    self.logger.info("failed to follow {}".format(screen_name))

            friends = self.get_friends()
            followers = self.get_followers()
            self.logger.info(
                "friends: {}, followers: {}".format(
                    len(friends), len(followers)
                )
            )

        self.basetime = now

        return False

    def utter(
        self,
        message: dict,
        master: dict
    ):
        return []

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

import requests
from requests_oauthlib import OAuth1

__all__ = ["Tumblr"]


class Tumblr:
    _BASE_URL = "https://api.tumblr.com/v2"

    def __init__(
            self,
            blog: str,
            client_key: str,
            client_secret: str,
            oauth_key: str,
            oauth_secret: str,
    ):
        """
        Nyaa!! OwO what's this? \*glomps you\*

        This is a supppper duper cool and awesome tumblr class!!1 It handles
        all sorts of heckin awesome things like authentication, posting,
        getting post info, and rebloging posts!

        :param blog: The name of the blog (one you have auth for)
        :param client_key: AKA Consumer Key
        :param client_secret: AKA Consumer Secret
        :param oauth_key: AKA Token
        :param oauth_secret: AKA Token Secret
        """
        self.blog = blog
        self._auth = OAuth1(client_key, client_secret, oauth_key, oauth_secret)

    def post(
            self,
            *,
            content: list[Mapping],
            tags: Iterable[str] = tuple(),
            **kwargs,
    ) -> Mapping[str, Any]:
        """
        Makes a super-duper tumblr post to your kawaii blog UwU

        See:
        https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param content: A list of content block type Mappings
        :param layout:
        :param tags: an optional list of tags
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        url = f"{self._BASE_URL}/blog/{self.blog}/posts"
        data = {
            "content": content,
            "tags": ", ".join(tags),
            **kwargs,
        }
        request = requests.post(url=url, json=data, auth=self._auth)
        request.raise_for_status()
        return request.json()

    def get_post(self, post_id: str | int, blog: str = None) -> Mapping:
        """
        Gets an awesome post from a hecking awesome blog OwO

        See:
        https://www.tumblr.com/docs/en/api/v2#postspost-id---fetching-a-post-neue-post-format

        :param post_id: The ID of the post
        :param blog: The blog for the post – defaults to the blog given to the
            tumblr object
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        if blog is None:
            blog = self.blog
        url = f"{self._BASE_URL}/blog/{blog}/posts/{post_id}"
        request = requests.get(url=url, auth=self._auth)
        request.raise_for_status()
        return request.json()

    def reblog(
            self,
            *,
            from_id: str | int,
            from_blog: str,
            content: list[Mapping],
            tags: Iterable[str] = tuple(),
    ) -> Mapping[str, Any]:
        """
        Does a super cool reglog on tumbler dot com!! ( – 3-)

        See:
        https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param from_id: The ID of the post to be rebloged from
        :param from_blog: The blog of the post to be rebloged from
        :param content: A list of content block type Mappings
        :param tags: an optional list of tags
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        parent_post = self.get_post(from_id, blog=from_blog)
        url = f"{self._BASE_URL}/blog/{self.blog}/posts"
        data = {
            "content": content,
            "tags": ", ".join(tags),
            "parent_tumblelog_uuid": parent_post["response"]["tumblelog_uuid"],
            "reblog_key": parent_post["response"]["reblog_key"],
            "parent_post_id": int(from_id),
        }
        request = requests.post(url=url, json=data, auth=self._auth)
        request.raise_for_status()
        return request.json()

    def poll_results(
            self,
            post_id: str | int,
            poll_id: str,
            blog: str = None,
    ) -> Mapping[str, Any]:
        """
        (OWO) !! Whats this? Poll results!

        Not defined in the API yet – seems to return a mapping of answer
        client_ids to the votes for each answer.

        :param post_id: The post that contains the poll
        :param poll_id: AKA the poll client_id
        :param blog: The blog for the post – defaults to the blog given to the
            tumblr object
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        if blog is None:
            blog = self.blog
        url = f"{self._BASE_URL}/polls/{blog}/{post_id}/{poll_id}/results"
        request = requests.get(url=url, auth=self._auth)
        request.raise_for_status()
        return request.json()

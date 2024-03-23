"""
Provides Tumblr, User, and Blog classes for interacting with various API
endpoints outlined in the Tumblr API documentation:
https://www.tumblr.com/docs/en/api/v2
"""

import json
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from io import StringIO
from types import MappingProxyType
from typing import Any, Mapping
from urllib.parse import quote_plus

import requests
from requests_oauthlib import OAuth1

from tumblr.content import *

__all__ = ["Tumblr", "User", "Blog"]

OPTIONAL_BLOG_FIELDS = (
    "is_following_you",
    "duration_blog_following_you",
    "duration_following_blog",
    "timezone",
    "timezone_offset",
)

StrMap = Mapping[str, Any]

BASE_URL = "https://api.tumblr.com/v2"
BLOG_URL = f"{BASE_URL}/blog"
USER_URL = f"{BASE_URL}/user"

mapping = MappingProxyType({})


class Tumblr:
    """
    Base tumblr class. Handles authentication and raw method calls.
    Exposes the generic "tagged" search feature.

    .. seealso::
        * https://www.tumblr.com/docs/en/api/v2#tagged-method

    Provides methods for the following endpoints:
        * /tagged – Get Posts with Tag

    :param client_key: AKA Consumer Key
    :param client_secret: AKA Consumer Secret
    :param oauth_key: AKA Token
    :param oauth_secret: AKA Token Secret
    """

    def __init__(
          self,
          client_key: str,
          client_secret: str,
          oauth_key: str,
          oauth_secret: str,
    ):
        self._auth = OAuth1(client_key, client_secret, oauth_key, oauth_secret)

    def tagged(
          self,
          tag: str,
          before: int = None,
          limit: int = 20,
          post_format: str = "HTML",
    ):
        """
        Retrieves posts with the given tag.

        See: https://www.tumblr.com/docs/en/api/v2#tagged-method

        :param tag: the search tag
        :param before: shows posts from before this timestamp
        :param limit: Number of posts to get (between 1–20)
        :param post_format: HTML, plain, or raw.
        """
        return self._get(
            f"{BASE_URL}/tagged",
            params={
                "tag": tag,
                "before": before,
                "limit": limit,
                "filter": post_format,
            }
        )

    def _get(self, url: str, params: Mapping = mapping):
        request = requests.get(url=url, auth=self._auth, params=params)
        request.raise_for_status()
        return request.json()

    def _delete(self, url: str, params: Mapping = mapping):
        request = requests.delete(url=url, auth=self._auth, params=params)
        request.raise_for_status()
        return request.json()

    def _put(self, url: str, params=None, files=None):
        params = {} if params is None else params
        if files is not None:
            content = StringIO(json.dumps(params))
            files = {"json": (None, content, "application/json"), **files}
            request = requests.put(url=url, auth=self._auth, files=files)
        else:
            request = requests.put(url=url, auth=self._auth, params=params)
        request.raise_for_status()
        return request.json()

    def _get_raw(self, url: str, params: Mapping = mapping):
        request = requests.get(url=url, auth=self._auth, params=params)
        request.raise_for_status()
        return request.content

    def _post(self, url: str, body=None, files=None):
        body = {} if body is None else body
        if files is not None:
            content = StringIO(json.dumps(body))
            files = {"json": (None, content, "application/json"), **files}
            request = requests.post(url=url, auth=self._auth, files=files)
        else:
            request = requests.post(url=url, auth=self._auth, json=body)
        request.raise_for_status()
        return request.json()


class User(Tumblr):
    """
    Provides methods for user-specific actions such as following, liking,
    and filtering tags

    .. seealso::
        - https://www.tumblr.com/docs/en/api/v2#user-methods

    Provides methods for the following endpoints:
        - /user/info – Get a User's Information
        - /user/limits – Get a User's Limits
        - /user/dashboard – Retrieve a User's Dashboard
        - /user/likes — Retrieve a User's Likes
        - /user/following – Retrieve the Blogs a User Is Following
        - /user/follow – Follow a blog
        - /user/unfollow – Unfollow a blog
        - /user/like – Like a Post
        - /user/unlike – Unlike a Post
        - /user/filtered_tags - Tag Filtering
        - /user/filtered_content - Content Filtering
    """

    def info(self):
        """
        Returns general information about the user.

        See: https://www.tumblr.com/docs/en/api/v2#userinfo--get-a-users-information
        """
        return self._get(url=f"{USER_URL}/info")

    def limits(self):
        """
        Returns general information about the user limits (posts, sideblogs,
        etc.)

        See: https://www.tumblr.com/docs/en/api/v2#userlimits--get-a-users-limits
        """
        return self._get(f"{USER_URL}/limits")

    def dashboard(self):
        """
        Retrieves the user's dashboard

        See: https://www.tumblr.com/docs/en/api/v2#userdashboard--retrieve-a-users-dashboard

        .. seealso::
            https://www.tumblr.com/docs/en/api_agreement
        """
        return self._get(f"{USER_URL}/dashboard")

    def likes(self):
        """
        Retrieves the post liked by the user

        See: https://www.tumblr.com/docs/en/api/v2#userlikes--retrieve-a-users-likes
        """
        return self._get(f"{USER_URL}/likes")

    def following(self):
        """
        Retrieves the blogs the user is following

        See: https://www.tumblr.com/docs/en/api/v2#userfollowing--retrieve-the-blogs-a-user-is-following
        """
        return self._get(f"{USER_URL}/following")

    def follow(self, url: str):
        """
        Follows a blog

        See: https://www.tumblr.com/docs/en/api/v2#userfollow--follow-a-blog

        :param url: The URL of the blog (can also be a blog name, e.g. "staff")
        """
        return self._post(f"{USER_URL}/follow", body={"url": url})

    def follow_email(self, email: str):
        """
        Follows a blog by email address. A blog is only followable by email
        if it has the ``Let people find your blogs through this address.``
        setting enabled on tumblr.com/settings/account.

        See: https://www.tumblr.com/docs/en/api/v2#userfollow--follow-a-blog

        :param email: The email of the user to follow
        """
        return self._post(f"{USER_URL}/follow", body={"email": email})

    def unfollow(self, url: str):
        """
        Unfollows a blog

        See: https://www.tumblr.com/docs/en/api/v2#userunfollow--unfollow-a-blog

        :param url: The URL of the blog (can also be a blog name, e.g. "staff")
        """
        return self._post(f"{USER_URL}/unfollow", body={"url": url})

    def like(self, post_id: str, from_blog: str):
        """
        Likes a post

        See: https://www.tumblr.com/docs/en/api/v2#userlike--like-a-post

        :param post_id: The ID of the post to like
        :param from_blog: The blog name of the blog that made the post
        """
        parent_post = self.get_post(post_id, from_blog)
        return self._post(
            f"{USER_URL}/like",
            body={
                "id": post_id,
                "reblog_key": parent_post["response"]["reblog_key"]
            }
        )

    def unlike(self, post_id: str, from_blog: str):
        """
        Unlikes a post

        See: https://www.tumblr.com/docs/en/api/v2#userunlike--unlike-a-post

        :param post_id: The ID of the post to like
        :param from_blog: The blog name of the blog that made the post
        """
        parent_post = self.get_post(post_id, from_blog)
        return self._post(
            f"{USER_URL}/unlike",
            body={
                "id": post_id,
                "reblog_key": parent_post["response"]["reblog_key"]
            }
        )

    def filtered_tags(self):
        """
        Retrieves the user's filtered tags

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_tags---tag-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering
        """
        return self._get(f"{USER_URL}/filtered_tags")

    def add_filtered_tags(self, tags: list[str]):
        """
        Adds the given tags to the user's filtered tags

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_tags---tag-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering

        :param tags: The tags to add to the filtered tags
        """
        return self._post(
            f"{USER_URL}/filtered_tags",
            body={"filtered_tags": tags}
        )

    def remove_filtered_tag(self, tag: str):
        """
        Removes the given tag from the user's filtered tags

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_tags---tag-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering

        :param tag: the tag to be removed
        """
        return self._delete(f"{USER_URL}/filtered_tags/{quote_plus(tag)}")

    def filtered_content(self):
        """
        Retrieves the user's list of filtered content

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_content---content-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering
        """
        return self._get(f"{USER_URL}/filtered_content")

    def add_filtered_content(self, filtered_content: str | list[str]):
        """
        Adds the given filtered content to the user's filtered content

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_content---content-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering

        :param filtered_content: one or more string to add to the
            filtered content
        """
        return self._post(
            f"{USER_URL}/filtered_content",
            body={"filtered_content": filtered_content}
        )

    def remove_filtered_content(self, filtered_content: str):
        """
        Removes the given content from the user's filtered content

        See: https://www.tumblr.com/docs/en/api/v2#userfiltered_content---content-filtering

        .. seealso::
            https://help.tumblr.com/hc/en-us/articles/115015814708-Tag-and-Post-Content-Filtering

        :param filtered_content: a string to remove from the filtered content
        """
        return self._delete(
            f"{USER_URL}/filtered_content",
            params={"filtered_content": filtered_content}
        )

    def get_post(
          self, post_id: str, from_blog: str, post_format: str = "npf",
    ) -> StrMap:
        """
        Retrieves a post

        See: https://www.tumblr.com/docs/en/api/v2#postspost-id---fetching-a-post-neue-post-format

        :param post_id: The ID of the post
        :param from_blog: The blog name of the blog that made the post
        :param post_format: The format to retrieve content: npf or legacy
        """
        return self._get(
            url=f"{BLOG_URL}/{from_blog}/posts/{post_id}",
            params={"post_format": post_format},
        )


class Blog(Tumblr):
    """
    Provides methods for blog-specific actions such as posting, and getting
    blog info.

    .. seealso::
        * https://www.tumblr.com/docs/en/api/v2#blog-methods

    Provides methods for the following endpoints:
        * /info - Retrieve Blog Info
        * /avatar — Retrieve a Blog Avatar
        * /blocks – Retrieve Blog's Blocks
        * /blocks – Block a Blog
        * /blocks/bulk – Block a list of Blogs
        * /blocks – Remove a Block
        * /likes — Retrieve Blog's Likes
        * /following — Retrieve Blog's following
        * /followers — Retrieve a Blog's Followers
        * /followed_by — Check If Followed By Blog
        * /posts/queue — Retrieve Queued Posts
        * /posts/queue/reorder — Reorder Queued Posts
        * /posts/queue/shuffle — Shuffle Queued Posts
        * /posts – Retrieve Published Posts
        * /posts/draft — Retrieve Draft Posts
        * /posts/submission — Retrieve Submission Posts
        * /notifications — Retrieve Blog's Activity Feed
        * /posts - Create/Reblog a Post
        * /posts/{post-id} - Fetching a Post
        * /posts/{post-id} - Editing a Post
        * /post/delete – Delete a Post
        * /posts/{post-id}/mute - Muting a Post's Notifications
        * /notes - Get notes for a specific Post

    Also includes support for undocumented Poll APIs:
        * /polls/{blog}/{post_id}/{poll_id}/results

    See the :meth:`poll_results` and :meth:`raw_poll_results` methods

    :param blog: The name of the blog (one you have auth for)
    :param client_key: AKA Consumer Key
    :param client_secret: AKA Consumer Secret
    :param oauth_key: AKA Token
    :param oauth_secret: AKA Token Secret
    """

    def __init__(
          self,
          blog: str,
          client_key: str,
          client_secret: str,
          oauth_key: str,
          oauth_secret: str
    ):
        super().__init__(client_key, client_secret, oauth_key, oauth_secret)
        self.blog = blog

    def info(self, fields: Iterable[str] = ()) -> StrMap:
        """
        Retrieves information about the blog

        See: https://www.tumblr.com/docs/en/api/v2#info---retrieve-blog-info

        :param fields: optional additional info fields that can be requested
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/info",
            params=blog_fields(fields),
        )

    def avatar(self, size: int = 64) -> bytes:
        """
        Retrieves the blog's avatar

        See: https://www.tumblr.com/docs/en/api/v2#avatar--retrieve-a-blog-avatar

        :param size: The nxn size of the image to download. Must be one of:
            16, 24, 30, 40, 48, 64, 96, 128, 512
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get_raw(url=f"{BLOG_URL}/{self.blog}/avatar/{size}")

    def blocks(
          self, offset: int = 0, limit: int = 20, fields: Iterable[str] = (),
    ) -> StrMap:
        """
        Retrieves this blog's blocked blogs

        See: https://www.tumblr.com/docs/en/api/v2#blocks--retrieve-blogs-blocks

        :param offset: The blocked blog number to start at
        :param limit: The number of blocked blogs to retrieve
            (between 1–20 inclusive)
        :param fields: Blog fields of the blocked blog to retrieve
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/blocks",
            params={"offset": offset, "limit": limit, **blog_fields(fields)},
        )

    def block(self, tumblelog: str = None, post_id: str = None) -> StrMap:
        """
        Blocks the specified blog or poster of the given ID

        See: https://www.tumblr.com/docs/en/api/v2#blocks--block-a-blog

        :param tumblelog: The blog identifier of the blog to block
        :param post_id: The post id of a post posted by the blog to block
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        params = {"blocked_tumblelog": tumblelog, "post_id": post_id}
        params = {k: v for k, v in params.items() if v is not None}
        if len(params) != 1:
            raise ValueError(
                "Exactly one of tumblelog or post_id must be given"
            )
        return self._post(url=f"{BLOG_URL}/{self.blog}/blocks", body=params)

    def bulk_block(self, tumblelogs: Iterable, force: bool = False) -> StrMap:
        """
        Blocks several blogs at once

        See: https://www.tumblr.com/docs/en/api/v2#blocksbulk--block-a-list-of-blogs

        :param tumblelogs: the blog identifiers of the blogs to block
        :param force: whether to force the block even if this cancels a Post+
            subscription
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._post(
            url=f"{BLOG_URL}/{self.blog}/blocks/bulk",
            body={"blocked_tumblelogs": ",".join(tumblelogs), "force": force}
        )

    def unblock(self, tumblelog: str = None, anonymous: bool = None) -> StrMap:
        """
        Unblocks a blog

        See: https://www.tumblr.com/docs/en/api/v2#blocks--remove-a-block

        :param tumblelog: The blog identifier of the blog to unblock
        :param anonymous: If tumblelog is not given and this is True, will
            unblock all anonymous blocks
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        params = {"blocked_tumblelog": tumblelog, "anonymous_only": anonymous}
        params = {k: v for k, v in params.items() if v is not None}
        if len(params) != 1:
            raise ValueError("One of tumblelog or anonymous must be given")
        return self._delete(url=f"{BLOG_URL}/{self.blog}/blocks", params=params)

    def likes(
          self,
          limit: int = None,
          offset: int = None,
          before: int = None,
          after: int = None,
          fields: Iterable[str] = (),
    ) -> StrMap:
        """
        Retrieves this blogs likes

        See: https://www.tumblr.com/docs/en/api/v2#likes--retrieve-blogs-likes

        :param limit: the number of likes to retrieve
        :param offset: the liked post to start at
        :param before: the timestamp of likes to retrieve before
        :param after: the timestamp of likes to retrieve after
        :param fields: the blog fields to retrieve with this request
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        params = {"limit": limit, "offset": offset,
                  "before": before, "after": after}
        params = {k: v for k, v in params.items() if v is not None}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/likes",
            params=params | blog_fields(fields),
        )

    def following(
          self, limit: int = 20, offset: int = 0, fields: Iterable[str] = ()
    ) -> StrMap:
        """
        Retrieves the blogs this blog follows

        See: https://www.tumblr.com/docs/en/api/v2#following--retrieve-blogs-following

        :param limit: the number of blogs to retrieve
        :param offset: the blog to start at
        :param fields: the blog fields to retrieve with this request
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/following",
            params={"limit": limit, "offset": offset, **blog_fields(fields)},
        )

    def followers(self, limit: int = 20, offset: int = 0) -> StrMap:
        """
        Retrieves the users following this blog

        See: https://www.tumblr.com/docs/en/api/v2#followers--retrieve-a-blogs-followers

        :param limit: the number of blogs to retrieve
        :param offset: the blog number to start at
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/followers",
            params={"limit": limit, "offset": offset},
        )

    def followed_by(self, blog: str):
        """
        Retrieves the following status of the given blog

        See: https://www.tumblr.com/docs/en/api/v2#followed_by--check-if-followed-by-blog

        :param blog: the blog that may be following this blog
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/followed_by",
            params={"query": blog},
        )

    def queue(
          self, offset: int = 0, limit: int = 20, post_format: str = "npf",
    ) -> StrMap:
        """
        Retrieves the list of currently queued posts

        See: https://www.tumblr.com/docs/en/api/v2#postsqueue--retrieve-queued-posts

        :param offset: the post number to start at
        :param limit: the number of posts to retrieve
        :param post_format: the post format: npf, HTML, text, raw
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        fmt = {"npf": True} if post_format == "npf" else {"filter": post_format}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/posts/queue",
            params={"offset": offset, "limit": limit, **fmt},
        )

    def reorder_queue(
          self, post_id: str | int, insert_after: str | int = 0) -> StrMap:
        """
        Reorders posts in the queue

        See: https://www.tumblr.com/docs/en/api/v2#postsqueuereorder--reorder-queued-posts

        :param post_id: the ID of the post to reorder
        :param insert_after: the id of the post to insert this post after
            or 0 to move to the top
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._post(
            url=f"{BLOG_URL}/{self.blog}/posts/queue/reorder",
            body={"post_id": post_id, "insert_after": insert_after}
        )

    def shuffle_queue(self):
        """
        Randomly shuffles the queue

        See: https://www.tumblr.com/docs/en/api/v2#postsqueueshuffle---shuffle-queued-posts

        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._post(url=f"{BLOG_URL}/{self.blog}/posts/queue/shuffle")

    def posts(
          self,
          post_type: str = None,
          post_id: int | str = None,
          tag: str | list[str] = None,
          limit: int = None,
          offset: int = None,
          reblog_info: bool = None,
          notes_info: bool = None,
          post_format: str = "npf",
          before: int = None,
          fields: Iterable[str] = (),
    ) -> StrMap:
        """
        Retrieves published posts

        See: https://www.tumblr.com/docs/en/api/v2#posts--retrieve-published-posts

        :param post_type: the type of post to return:
            text, quote, link, answer, video, audio, photo, chat
        :param post_id: the ID of a specific post
        :param tag: one or more tags to filter by
        :param limit: the number of posts to retrieve
        :param offset: the post number to start at
        :param reblog_info: whether to return reblog information
        :param notes_info: whether to return notes information
        :param post_format: the post format to return: HTML, text, raw, or npf
        :param before: retrieves posts before this timestamp
        :param fields: the blog fields to retrieve
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        params = {
            "post_type": post_type, "post_id": post_id, "tag": tag,
            "limit": limit, "offset": offset, "reblog_info": reblog_info,
            "notes_info": notes_info, "before": before,
        }
        params = {k: v for k, v in params.items() if v is not None}
        fmt = {"npf": True} if post_format == "npf" else {"filter": post_format}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/posts",
            params=params | fmt | blog_fields(fields),
        )

    def drafts(
          self,
          before_id: int | str = 0,
          post_format: str = "npf",
          fields: Iterable[str] = (),
    ) -> StrMap:
        """
        Retrieves drafted posts

        See: https://www.tumblr.com/docs/en/api/v2#postsdraft--retrieve-draft-posts

        :param before_id: gets posts created before the post with the given ID
        :param post_format: the post format to retrieve: npf, HTML, text, raw
        :param fields: the blog fields to retrieve
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        fmt = {"npf": True} if post_format == "npf" else {"filter": post_format}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/posts/draft",
            params={"before_id": before_id} | fmt | blog_fields(fields)
        )

    def submissions(
          self,
          offset: int | str = 0,
          post_format: str = "npf",
          fields: Iterable[str] = (),
    ) -> StrMap:
        """
        Retrieves post submissions

        See: https://www.tumblr.com/docs/en/api/v2#postssubmission--retrieve-submission-posts

        :param offset: the post offset
        :param post_format: the post format to retrieve: npf, HTML, text, raw
        :param fields: the blog fields to retrieve
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        fmt = {"npf": True} if post_format == "npf" else {"filter": post_format}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/posts/submission",
            params={"offset": offset} | fmt | blog_fields(fields)
        )

    def notifications(
          self,
          before: int = None,
          types: Iterable[str] = None,
          rollups: bool = None,
          omit_post_ids: Iterable[str] = None,
    ) -> StrMap:
        """
        Retrieves the blog's activity feed

        See: https://www.tumblr.com/docs/en/api/v2#notifications--retrieve-blogs-activity-feed

        :param before: a timestamp to retrieve notifications before
        :param types: one or more notification types to filter by (see API docs)
        :param rollups: whether similar activity should be grouped
        :param omit_post_ids: an array of post IDs to omit
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        params = {"before": before, "types": types,
                  "rollups": rollups, "omit_post_ids": omit_post_ids}
        params = {k: v for k, v in params.items() if v is not None}
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/notifications",
            params=params,
        )

    def get_post(
          self, post_id: str, from_blog: str = None, post_format: str = "npf",
    ) -> StrMap:
        """
        Retrieves a specific post

        See: https://www.tumblr.com/docs/en/api/v2#postspost-id---fetching-a-post-neue-post-format

        :param post_id: the ID of the desired post
        :param from_blog: the blog that made the post
            (the current blog if not provided)
        :param post_format: the post format to retrieve: npf, HTML, text, raw
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{from_blog or self.blog}/posts/{post_id}",
            params={"post_format": post_format},
        )

    def post(
          self,
          content: Iterable[Block],
          state: str = None,
          publish_on: str = None,
          date: str = None,
          tags: Iterable[str] = (),
          source_url: str = None,
          send_to_twitter: bool = None,
          is_private: bool = None,
          slug: str = None,
          interactability_reblog: str = None,
    ) -> StrMap:
        """
        Creates a new post

        See: https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param content: the content blocks of the post's body
        :param state: the state to post in:
            published, queue, draft, private, unapproved
        :param publish_on: if the publish-state is "queue", will use this
            ISO 8601 format timestamp as the publish date
        :param date: the ISO 8601 format datetime to backdate the post
        :param tags: an iterable of tags to give the post
        :param source_url: a source attribution for the post content
        :param send_to_twitter: whether to share this post to a connected
            Twitter account
        :param is_private: whether the post, if it is an answer,
            should be a private
        :param slug: Custom URL for the post
        :param interactability_reblog: who can interact with this post:
            everyone, or noone
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        content = _process_blocks(content)
        params = {
            "content": content.blocks,
            "layout": content.layout,
            "state": state,
            "publish_on": publish_on,
            "date": date,
            "tags": ", ".join(tags),
            "source_url": source_url,
            "send_to_twitter": send_to_twitter,
            "is_private": is_private,
            "slug": slug,
            "interactability_reblog": interactability_reblog,
        }
        return self._post(
            url=f"{BLOG_URL}/{self.blog}/posts",
            body={k: v for k, v in params.items() if v is not None},
            files=content.files,
        )

    def reblog(
          self,
          from_id: str | int,
          content: Iterable[Block],
          from_blog: str = None,
          state: str = None,
          publish_on: str = None,
          date: str = None,
          tags: Iterable[str] = (),
          source_url: str = None,
          send_to_twitter: bool = None,
          is_private: bool = None,
          slug: str = None,
          interactability_reblog: str = None,
    ):
        """
        Creates a reblog

        See: https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param from_id: the post ID to reblog
        :param content: the content blocks of the post's body
        :param from_blog: the blog that made the reblogged post
        :param state: the state to post in:
            published, queue, draft, private, unapproved
        :param publish_on: if the publish-state is "queue", will use this
            ISO 8601 format timestamp as the publish date
        :param date: the ISO 8601 format datetime to backdate the post
        :param tags: an iterable of tags to give the post
        :param source_url: a source attribution for the post content
        :param send_to_twitter: whether to share this post to a connected
            Twitter account
        :param is_private: whether the post, if it is an answer,
            should be a private
        :param slug: Custom URL for the post
        :param interactability_reblog: who can interact with this post:
            everyone, or noone
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        parent_post = self.get_post(from_id, from_blog)
        content = _process_blocks(content)
        params = {
            "content": content.blocks,
            "layout": content.layout,
            "parent_tumblelog_uuid": parent_post["response"]["tumblelog_uuid"],
            "reblog_key": parent_post["response"]["reblog_key"],
            "parent_post_id": int(from_id),
            "state": state,
            "publish_on": publish_on,
            "date": date,
            "tags": ", ".join(tags),
            "source_url": source_url,
            "send_to_twitter": send_to_twitter,
            "is_private": is_private,
            "slug": slug,
            "interactability_reblog": interactability_reblog,
        }
        return self._post(
            url=f"{BLOG_URL}/{self.blog}/posts",
            body={k: v for k, v in params.items() if v is not None},
            files=content.files,
        )

    # TODO – figure out what is going on with this
    def edit_post(
          self,
          post_id: str | int,
          content: Iterable[Block] = None,
          state: str = None,
          publish_on: str = None,
          date: str = None,
          tags: Iterable[str] = (),
          source_url: str = None,
          send_to_twitter: bool = None,
          is_private: bool = None,
          slug: str = None,
          interactability_reblog: str = None,
    ):
        """
        Edits an existing post

        See: https://www.tumblr.com/docs/en/api/v2#postspost-id---editing-a-post-neue-post-format

        :param post_id: the ID of the post to edit (posted by the current blog)
        :param content: the content blocks of the post's body
        :param state: the state to post in:
            published, queue, draft, private, unapproved
        :param publish_on: if the publish-state is "queue", will use this
            ISO 8601 format timestamp as the publish date
        :param date: the ISO 8601 format datetime to backdate the post
        :param tags: an iterable of tags to give the post
        :param source_url: a source attribution for the post content
        :param send_to_twitter: whether to share this post to a connected
            Twitter account
        :param is_private: whether the post, if it is an answer,
            should be a private
        :param slug: Custom URL for the post
        :param interactability_reblog: who can interact with this post:
            everyone, or noone
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        post = self.get_post(post_id)["response"]
        content = _process_blocks(content) if content is not None else None
        params = {
            "content": content.blocks if content else None,
            "layout": content.layout if content else None,
            "parent_tumblelog_uuid": post.get("tumblelog_uuid"),
            "reblog_key": post.get("reblog_key"),
            "parent_post_id": post.get("parent_post_id"),
            "state": state,
            "publish_on": publish_on,
            "date": date,
            "tags": ", ".join(tags) if tags else None,
            "source_url": source_url,
            "send_to_twitter": send_to_twitter,
            "is_private": is_private,
            "slug": slug,
            "interactability_reblog": interactability_reblog,
        }
        post = {**post, "tags": ", ".join(post["tags"])}
        params = {k: v for k, v in params.items() if k in post}
        post = {k: v for k, v in post.items() if k in params}
        params = {k: v for k, v in params.items() if v is not None}
        return self._put(
            url=f"{BLOG_URL}/{self.blog}/posts/{post_id}",
            params=post | params,
            files=content.files if content else None
        )

    def delete_post(self, post_id: str | int) -> StrMap:
        """
        Deletes a post posted by this blog

        See: https://www.tumblr.com/docs/en/api/v2#postdelete--delete-a-post

        :param post_id: the ID of the post to delete
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._delete(
            url=f"{BLOG_URL}/{self.blog}/post/delete",
            params={"id": post_id},
        )

    def mute_post(
          self,
          post_id: str | int,
          mute_length_seconds: int = 0,
    ) -> StrMap:
        """
        Mutes notifications for a post

        See: https://www.tumblr.com/docs/en/api/v2#postspost-idmute---muting-a-posts-notifications

        :param post_id: the ID of the post to mute
        :param mute_length_seconds: the time the post should remain muted
            (0 for forever)
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._post(
            url=f"{BLOG_URL}/{self.blog}/posts/{post_id}/mute",
            body={"mute_length_seconds": mute_length_seconds},
        )

    def unmute_post(self, post_id: str | int) -> StrMap:
        """
        Unmutes the notifications for a post

        See: https://www.tumblr.com/docs/en/api/v2#postspost-idmute---muting-a-posts-notifications

        :param post_id: the ID of the post to unmute
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._delete(url=f"{BLOG_URL}/{self.blog}/posts/{post_id}/mute")

    def notes(
          self, post_id: str | int, before: int = None, mode: str = "all",
    ) -> StrMap:
        """
        Retrieves the notes for a specific post

        See: https://www.tumblr.com/docs/en/api/v2#notes---get-notes-for-a-specific-post

        :param post_id: the ID of the post
        :param before: the timestamp in seconds to retrieve notes before
        :param mode: the type of note to retrieve (see API docs)
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        return self._get(
            url=f"{BLOG_URL}/{self.blog}/notes",
            params={"id": post_id, "before_timestamp": before, "mode": mode}
        )

    def poll_results(
          self,
          post_id: str | int,
          blog: str = None,
    ) -> StrMap:
        """
        Returns a poll object zipped with answer text. Finds the first poll
        in the given post and returns its results + labels

        :param post_id: The post that contains the poll
        :param blog: The blog for the post – defaults to the blog given to the
            Blog object
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        if blog is None:
            blog = self.blog
        poll = get_polls_from_post(self.get_post(post_id, from_blog=blog))
        poll_id = poll["client_id"]
        results = self._get(
            f"{BASE_URL}/polls/{blog}/{post_id}/{poll_id}/results"
        )
        return zip_poll_with_results(poll, results)

    def raw_poll_results(
          self,
          post_id: str | int,
          poll_id: str,
          blog: str = None,
    ) -> StrMap:
        """
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
        url = f"{BASE_URL}/polls/{blog}/{post_id}/{poll_id}/results"
        return self._get(url)


def zip_poll_with_results(
      poll: Mapping[str, Any],
      results: Mapping[str, Any]
) -> Mapping[str, Any]:
    """
    Utility function that combines poll data with the poll results.

    Returns a new mapping with a "total_votes" key mapping to the total
    number of votes and each poll answer has a "votes" key mapping to the
    number of votes for that answer.

    :param poll: the poll block data
    :param results: the result data (either the response or response data)
    :return: a new mapping with the poll data
    """
    if "response" in results:
        results = results["response"]
    results = results["results"]
    poll = {**deepcopy(poll)}
    for answer in poll["answers"]:
        vote = results[answer["client_id"]]
        answer["votes"] = vote
    poll["total_votes"] = sum(results.values())
    return poll


def get_polls_from_post(post: Mapping) -> Mapping[str, Any] | None:
    """
    Convenience function that retrieves the first poll block from a post.

    There are a few posts that contain more than one poll in the post-text;
    however, these are few and far between and cannot be posted any more.

    :param post: The content of the post or the response from getting a post
    :return: An iterator of the poll block mappings
    """
    if "response" in post:
        post = post["response"]
    for block in post["content"]:
        if block["type"] == "poll":
            return block


@dataclass
class _Content:
    blocks: Iterable[Mapping]
    layout: list[Mapping]
    files: Mapping


def _process_blocks(blocks: Iterable[Block]) -> _Content:
    block_data = []
    layout = {"type": "rows", "display": []}
    files = {}
    for block in blocks:
        new_blocks = []
        match block:
            case ContentBlock() as content:
                new_blocks = [content.data()]
            case MultiBlock() as multi:
                new_blocks = [b.data for b in multi.data]
            case DataBlock() as data:
                new_blocks = [data.data()]
                files |= data.file()
            case ReadMore():
                layout["truncate_after"] = len(block_data) - 1
            case Row(images=images):
                for image in images:
                    new_blocks.append(image.data())
                    files |= image.file()
        if new_blocks:
            block_layout = [i + len(block_data) for i in range(len(new_blocks))]
            layout["display"].append({"blocks": block_layout})
            block_data.extend(new_blocks)
    return _Content(
        blocks=block_data,
        layout=[layout],
        files=files,
    )


def blog_fields(fields):
    fields = [
        f"?{field}" if field in OPTIONAL_BLOG_FIELDS else field
        for field in fields
    ]
    return {"fields[blogs]": ",".join(fields)} if fields else {}

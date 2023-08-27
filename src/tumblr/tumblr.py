"""
Nyah~~~ A super kawaii module containing the tumblr class and post utilities
"""

import json
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from io import StringIO
from typing import Any, Iterator, Mapping

import requests
from requests_oauthlib import OAuth1

from tumblr.content import *

__all__ = ["Tumblr", "zip_poll_with_results", "get_polls_from_post"]


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
          content: Iterable[Block],
          tags: Iterable[str] = tuple(),
          **kwargs,
    ) -> Mapping[str, object]:
        """
        Makes a super-duper tumblr post to your kawaii blog UwU

        See:
        https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param content: the post content
        :param tags: an optional list of tags
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        url = f"{self._BASE_URL}/blog/{self.blog}/posts"
        content = _process_blocks(content)
        params = {
            "content": content.blocks,
            "layout": content.layout,
            "tags": ", ".join(tags),
            **kwargs,
        }
        return _post(url, self._auth, params, content.files)

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
        return _get(url, self._auth)

    def reblog(
          self,
          *,
          from_id: str | int,
          from_blog: str = None,
          content: Iterable[Block],
          tags: Iterable[str] = tuple(),
          to_blog=None,
    ) -> Mapping[str, Any]:
        """
        Does a super cool reglog on tumbler dot com!! ( – 3-)

        See:
        https://www.tumblr.com/docs/en/api/v2#posts---createreblog-a-post-neue-post-format

        :param from_id: The ID of the post to be rebloged from
        :param from_blog: The blog of the post to be rebloged from
        :param content: A list of content block type Mappings
        :param tags: an optional list of tags
        :param to_blog: The blog for the reblog to be posted to
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        parent_post = self.get_post(from_id, blog=from_blog)
        url = f"{self._BASE_URL}/blog/{to_blog or self.blog}/posts"
        content = _process_blocks(content)
        data = {
            "content": content.blocks,
            "layout": content.layout,
            "tags": ", ".join(tags),
            "parent_tumblelog_uuid": parent_post["response"]["tumblelog_uuid"],
            "reblog_key": parent_post["response"]["reblog_key"],
            "parent_post_id": int(from_id),
        }
        return _post(url, self._auth, data, content.files)

    def poll_results(
          self,
          post_id: str | int,
          blog: str = None,
    ) -> Mapping[str, Any]:
        """
        (OWO) !! What's this? Poll results!

        Returns a poll object zipped with answer text. Finds the first poll
        in the given post and returns its results + labels

        :param post_id: The post that contains the poll
        :param blog: The blog for the post – defaults to the blog given to the
            tumblr object
        :return: The JSON encoded response

        :raises HTTPError: if the request fails
        """
        if blog is None:
            blog = self.blog
        poll = next(get_polls_from_post(self.get_post(post_id)))
        poll_id = poll["client_id"]
        url = f"{self._BASE_URL}/polls/{blog}/{post_id}/{poll_id}/results"
        results = _get(url, self._auth)
        return zip_poll_with_results(poll, results)

    def raw_poll_results(
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
        return _get(url, self._auth)


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


def get_polls_from_post(post: Mapping) -> Iterator[Mapping[str, Any]]:
    """
    Convenience function that retrieves the poll blocks from a post.

    :param post: The content of the post or the response from getting a post
    :return: An iterator of the poll block mappings
    """
    if "response" in post:
        post = post["response"]
    for block in post["content"]:
        if block["type"] == "poll":
            yield block


def _get(url, auth):
    request = requests.get(url=url, auth=auth)
    request.raise_for_status()
    return request.json()


def _post(url, auth, content, files):
    if files:
        content = StringIO(json.dumps(content))
        files = {"json": (None, content, "application/json"), **files}
        request = requests.post(url=url, auth=auth, files=files)
    else:
        request = requests.post(url=url, auth=auth, json=content)
    request.raise_for_status()
    return request.json()


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

from collections.abc import Iterator, Mapping
from copy import deepcopy
from typing import Any

__all__ = ["zip_poll_with_results", "get_polls_from_post"]


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

    It seems it is not *impossible* to have more than one poll per post –
    despite the tumblr client seeming to enforce this on the front-end side.

    :param post: The content of the post or the response from getting a post
    :return: An iterator of the poll block mappings
    """
    if "response" in post:
        post = post["response"]
    for block in post["content"]:
        if block["type"] == "poll":
            yield block

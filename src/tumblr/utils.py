from collections.abc import Mapping
from copy import deepcopy
from typing import Any


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

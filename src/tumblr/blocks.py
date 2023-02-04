from collections.abc import Mapping
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

__all__ = [
    "poll",
    "raw_text",
    "text",
    "heading",
    "subheading",
    "cursive",
    "quote",
    "indented",
    "chat",
    "ordered_list",
    "ordered_list_item",
    "unordered_list",
    "unordered_list_item",
]


def poll(
        question: str,
        options: list[str],
        *,
        expire_after=timedelta(seconds=604800),
        poll_uuid: UUID = None,
        option_uuids: list[UUID] = None,
) -> Mapping[str, Any]:
    """
    Returns a poll content block.
    This is not officially documented yet so who knows if it's going to change!

    :param question: The Poll prompt
    :param options: The poll options
    :param expire_after: a time delta of when the poll will close
    :param poll_uuid: an optional UUID4 – one will be generated if not given
    :param option_uuids: an optional list of UUID4s – a list will be generated
        if not given. Raises a Value error if the number of options does not
        match the number of given option UUIDs

    :raises ValueError: If the option_uuids are given does not match the
        number of options.
    """
    if option_uuids is None:
        option_uuids = [uuid4() for _ in options]
    return {
        "type": "poll",
        "question": question,
        "client_id": str(uuid4() if poll_uuid is None else poll_uuid),
        "answers": [
            {"answer_text": answer,
             "client_id": str(answer_uuid)}
            for answer, answer_uuid in zip(options, option_uuids, strict=True)
        ],
        'settings': {
            'close_status': 'closed-after',
            'expire_after': expire_after.total_seconds(),
            'multiple_choice': False,
        },
    }


def raw_text(content: str, **kwargs) -> Mapping:
    """
    Returns a Mapping of the form: {"type": "text", "text": content}
    With any additional kwargs given to the function.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return {
        "type": "text",
        "text": content,
        **kwargs,
    }


def text(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a Text content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, **kwargs)


def heading(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a Heading1 Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="heading1", **kwargs)


def subheading(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a Heading2 Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="heading2", **kwargs)


def cursive(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a quirky Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="quirky", **kwargs)


def quote(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a quote Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="quote", **kwargs)


def indented(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns an indented Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="indented", **kwargs)


def chat(content: str, **kwargs) -> Mapping[str: Any]:
    """
    Returns a chat Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(content, subtype="chat", **kwargs)


def ordered_list(content: list[str], **kwargs) -> list[Mapping[str: Any]]:
    """
    Returns a list of ordered-list-item Text subtype content blocks with the
    given items in the content list.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    """Must be unpacked in the content list"""
    return [
        raw_text(item, subtype="ordered-list-item", **kwargs)
        for item in content
    ]


def ordered_list_item(item, **kwargs) -> Mapping[str: Any]:
    """
    Returns an ordered-list-item Text subtype content block with the given
    content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(item, subtype="ordered-list-item", **kwargs)


def unordered_list(content: list[str], **kwargs) -> list[Mapping[str: Any]]:
    """
    Returns a list of unordered-list-item Text subtype content blocks with the
    given items in the content list.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    """Must be unpacked in the content list"""
    return [
        raw_text(item, subtype="unordered-list-item", **kwargs)
        for item in content
    ]


def unordered_list_item(item, **kwargs) -> Mapping[str: Any]:
    """
    Returns an unordered-list-item Text subtype content block with the given
    content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    return raw_text(item, subtype="unordered-list-item", **kwargs)

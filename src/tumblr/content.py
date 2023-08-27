"""
OwO !! What's this?! A sugoi way to make post content UwU Nyah!
"""

import abc
from collections.abc import Iterable, Mapping
from datetime import timedelta
from io import BytesIO
from pathlib import PurePath
from uuid import uuid4

__all__ = [
    "Block",
    "ContentBlock",
    "MultiBlock",
    "DataBlock",
    "RawText",
    "Text",
    "Heading",
    "Subheading",
    "Cursive",
    "Quote",
    "Chat",
    "OrderedListItem",
    "UnorderedListItem",
    "OrderedList",
    "UnorderedList",
    "Poll",
    "Image",
    "ReadMore",
    "Row",
]


class Block(abc.ABC):
    ...


class ContentBlock(Block, abc.ABC):
    @abc.abstractmethod
    def data(self) -> Mapping:
        ...


class MultiBlock(Block, abc.ABC):
    @abc.abstractmethod
    def data(self) -> Iterable[Mapping]:
        ...


class DataBlock(Block, abc.ABC):
    def __init__(self, path: PurePath | str, mime_type: str):
        self.path = path
        self.mime_type = mime_type
        self.fid = str(uuid4())

    def file(self):
        with open(self.path, "rb") as f:
            byte_data = BytesIO(f.read())
        return {self.fid: (self.fid, byte_data, self.mime_type)}


class RawText(ContentBlock):
    def __init__(self, content: str, subtype: str, **kwargs):
        self.content = content
        self.subtype = subtype
        self.kwargs = kwargs

    def data(self) -> Mapping:
        return {
            "type": "text",
            "text": self.content,
            "subtype": self.subtype,
            **self.kwargs,
        }


class Text(ContentBlock):
    """
    A Text content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """
    def __init__(self, content: str, **kwargs):
        self.content = content
        self.kwargs = kwargs

    def data(self):
        return {
            "type": "text",
            "text": self.content,
            **self.kwargs,
        }


class Heading(RawText):
    """
    A Heading1 Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "heading1", **kwargs)


class Subheading(RawText):
    """
    A Heading2 Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "heading2", **kwargs)


class Cursive(RawText):
    """
    A quirky Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "quirky", **kwargs)


class Quote(RawText):
    """
    A quote Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "quote", **kwargs)


class Indented(RawText):
    """
    An indented Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "indented", **kwargs)


class Chat(RawText):
    """
    A chat Text subtype content block with the given content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "chat", **kwargs)


class OrderedListItem(RawText):
    """
    An ordered-list-item Text subtype content block with the given
    content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "ordered-list-item", **kwargs)


class UnorderedListItem(RawText):
    """
    An unordered-list-item Text subtype content block with the given
    content.

    See: https://www.tumblr.com/docs/npf#content-block-type-text
    """

    def __init__(self, content: str, **kwargs):
        super().__init__(content, "unordered-list-item", **kwargs)


class OrderedList(MultiBlock):
    """
    A list of ordered-list-item Text subtype content blocks with the
    given items in the content list. Passes all kwargs onto each
    individual list item.
    """

    def __init__(self, items: list[str], **kwargs):
        self.items = [OrderedListItem(item, **kwargs) for item in items]

    def data(self):
        yield from (item.data() for item in self.items)


class UnorderedList(MultiBlock):
    """
    A list of unordered-list-item Text subtype content blocks with the
    given items in the content list. Passes all kwargs onto each
    individual list item.
    """

    def __init__(self, items: list[str], **kwargs):
        self.items = [UnorderedListItem(item, **kwargs) for item in items]

    def data(self):
        yield from (item.data() for item in self.items)


class Poll(ContentBlock):
    """
    A poll content block.
    This is not officially documented yet so who knows if it's going to
    change!

    .. note::
        - expire_after is clamped between 1 and 7 days serverside
        - Only one poll can be in each post and this is enforced serverside
        - At least 2 and at most 12 options can be provided each having a
          max of 80 characters.

    :param question: The Poll prompt
    :param options: The poll options
    :param expire_after: a time delta of when the poll will close
        (default 7 days)
    """

    def __init__(
          self,
          question: str,
          options: Iterable[str],
          *,
          expire_after: timedelta = timedelta(days=7),
    ):
        self.question = question
        self.options = options
        self.expire_after = expire_after

    def data(self) -> Mapping:
        return {
            "type": "poll",
            "question": self.question,
            # must be provided in request but are now ignored
            "client_id": str(uuid4()),
            "answers": [
                {"answer_text": answer, "client_id": str(uuid4())}
                for answer in self.options
            ],
            'settings': {
                'close_status': 'closed-after',
                'expire_after': int(self.expire_after.total_seconds()),
            },
        }


class Image(DataBlock):
    """
    An Image block.

    See: https://www.tumblr.com/docs/npf#content-block-type-image

    :param path: The path to the image
    :param img_type: The image MIME type
    :param alt_text: Image Alt Text
    :param caption: Optional Caption (displayed under image when viewed)
    """

    def __init__(
          self,
          path: PurePath | str,
          img_type: str,
          alt_text: str,
          caption: str = None,
    ):
        super().__init__(path, img_type)
        self.alt_text = alt_text
        self.caption = caption

    def data(self) -> Mapping:
        return {
            "type": "image",
            "media": [{"type": self.mime_type, "identifier": self.fid}],
            "alt_text": self.alt_text,
            "caption": self.caption,
        }


class ReadMore(Block):
    """
    Inserts a "keep reading" bar that truncates the post.
    Only one can be added per post.

    See: https://www.tumblr.com/docs/npf#read-more
    """


class Row(Block):
    """
    Creates a row of images.

    :param images: varargs of Image blocks.
    """
    def __init__(self, *images: Image):
        self.images = images

    def data(self) -> Iterable[Mapping]:
        yield from (image.data() for image in self.images)

from collections.abc import Mapping
from datetime import timedelta
from pathlib import PurePath
from typing import Iterable, Self

__all__ = ["Content"]

from uuid import uuid4


class Content:
    def __init__(self):
        self.blocks = []
        self._rows = {
            "type": "rows",
            "display": []
        }
        self.files = {}

    @property
    def layout(self):
        """The layout information of the post content"""
        return [self._rows]

    @property
    def _idx(self):
        return len(self.blocks) - 1

    @property
    def _display(self):
        return self._rows["display"]

    @property
    def _next_fid(self):
        return f"data-{len(self.files):02d}"

    def text(self, content, **kwargs) -> Self:
        """
        A Text content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        text_data = {
            "type": "text",
            "text": content,
            **kwargs,
        }
        self.blocks.append(text_data)
        self._display.append(_block(self._idx))
        return self

    def heading(self, content: str, **kwargs) -> Self:
        """
        A Heading1 Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="heading1", **kwargs)

    def subheading(self, content: str, **kwargs) -> Self:
        """
        A Heading2 Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="heading2", **kwargs)

    def cursive(self, content: str, **kwargs) -> Self:
        """
        A quirky Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="quirky", **kwargs)

    def quote(self, content: str, **kwargs) -> Self:
        """
        A quote Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="quote", **kwargs)

    def indented(self, content: str, **kwargs) -> Self:
        """
        An indented Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="indented", **kwargs)

    def chat(self, content: str, **kwargs) -> Self:
        """
        A chat Text subtype content block with the given content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(content, subtype="chat", **kwargs)

    def ordered_list(self, *content: str, **kwargs) -> Self:
        """
        A list of ordered-list-item Text subtype content blocks with the
        given items in the content list. Passes all kwargs onto each
        individual list item.
        """
        for item in content:
            self.ordered_list_item(item, **kwargs)
        return self

    def unordered_list(self, *content: str, **kwargs) -> Self:
        """
        A list of unordered-list-item Text subtype content blocks with the
        given items in the content list. Passes all kwargs onto each
        individual list item.
        """
        for item in content:
            self.unordered_list_item(item, **kwargs)
        return self

    def ordered_list_item(self, item, **kwargs) -> Self:
        """
        An ordered-list-item Text subtype content block with the given
        content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(item, subtype="ordered-list-item", **kwargs)

    def unordered_list_item(self, item, **kwargs):
        """
         An unordered-list-item Text subtype content block with the given
        content.

        See: https://www.tumblr.com/docs/npf#content-block-type-text
        """
        return self.text(item, subtype="unordered-list-item", **kwargs)

    def poll(
            self,
            question: str,
            options: list[str],
            *,
            expire_after=timedelta(days=7),
    ) -> Self:
        """
        A poll content block.
        This is not officially documented yet so who knows if it's going to
        change!

        .. note::
            - expire_after is clamped between 1 and 7 days serverside
            - Only one poll can be in each post and this is enforced serverside
            - At least 2 and at most 10 options can be provided each having a
              max of 80 characters.

        :param question: The Poll prompt
        :param options: The poll options
        :param expire_after: a time delta of when the poll will close
            (default 7 days)
        """
        poll_data = {
            "type": "poll",
            "question": question,
            # must be provided in request but are now ignored
            "client_id": str(uuid4()),
            "answers": [
                {"answer_text": answer, "client_id": str(uuid4())}
                for answer in options
            ],
            'settings': {
                'close_status': 'closed-after',
                'expire_after': expire_after.total_seconds(),
                'multiple_choice': False,
            },
        }
        self.blocks.append(poll_data)
        self._display.append(_block(self._idx))
        return self

    def image(
            self,
            path: PurePath | str,
            img_type: str,
            alt_text: str,
            caption: str = None
    ) -> Self:
        """
        An Image block.

        See: https://www.tumblr.com/docs/npf#content-block-type-image

        :param path: The path to the image
        :param img_type: The image MIME type
        :param alt_text: Image Alt Text
        :param caption: Optional Caption (display under image when viewed)
        """
        fid = self._next_fid
        file = open(path, "rb")
        self.files[fid] = (fid, file, img_type)
        data = {
            "type": "image",
            "media": [{"type": img_type, "identifier": fid}],
            "alt_text": alt_text,
            "caption": caption,
        }
        self.blocks.append(data)
        self._display.append(_block(self._idx))
        return self

    def read_more(self) -> Self:
        """
        Inserts a "keep reading" bar that truncates the post.

        See: https://www.tumblr.com/docs/npf#read-more

        :raises ValueError: if a read more has already been inserted into the
            content
        """
        if "truncate_after" in self._rows:
            raise ValueError("Only one read more per post :(")
        else:
            self._rows["truncate_after"] = self._idx
        return self

    def row_of(self, *image_data: Mapping[str, str] | Iterable[str]) -> Self:
        """
        Creates a row of images.

        :param image_data: either a mapping of image param names to values, or
            an iterable of the image params.
        """
        blocks = []
        for image in image_data:
            if isinstance(image, Mapping):
                self.image(**image)
            else:
                self.image(*image)
            blocks.append(self._display.pop()["blocks"][0])
        self._display.append(_block(blocks))
        return self


def _row_layout():
    return {
        "type": "rows",
        "display": []
    }


def _block(idx):
    return {
        "blocks": [idx] if isinstance(idx, int) else idx
    }

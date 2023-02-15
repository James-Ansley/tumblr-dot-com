# Tumblr-Dot-Com

> OwO What's this?! Nyaa!!1

Did that big bad ewong mwsk make twittew apis cowst money :( why not come to
tumbler?!

This is a quick and dirty tumblr API wrapper I have made to help with another
project I am working on. Currently, a WIP but still usable.

Includes support for polls.

## Install

```
pip install tumblrdotcom
```

## Usage

Provides a `tumblr.Tumblr` class. See https://www.tumblr.com/docs/en/api/v2 for
API details relating to data formatting.
Also provides a `tumblr.Content` class to assist in generating text post
content as well as utility functions in `tumblr.utils` to process poll data.

### Example

```python
import os
from datetime import timedelta
from pprint import pprint

from tumblr import Content, Tumblr

tumblr = Tumblr(
    blog="pizza",  # or 'pizza.tumblr.com'
    client_key=os.getenv("CONSUMER_KEY"),
    client_secret=os.getenv("CONSUMER_SECRET"),
    oauth_key=os.getenv("OAUTH_TOKEN"),
    oauth_secret=os.getenv("OAUTH_SECRET"),
)

response = tumblr.post(
    content=(
        Content()
        .heading("Hello, World!")
        .text("Oh boy! Isn't it great to have a tumblr!")
        .row_of(
            (
                "clown_left.jpg",
                "image/jpeg",
                "A photo clown holding their right thumb up towards the camera"
            ),
            (
                "clown_right.jpg",
                "image/jpeg",
                "A photo clown holding their left thumb up towards the camera"
            )
        )
        .poll(
            "Don't you think so?",
            ["Yes", "No"],
            expire_after=timedelta(days=1),
        )
    ),
    tags=["pizza", "I can't even remember why they were deleted"],
)

pprint(response)
```

## API

### `tumblr.Tumblr`

```
def __init__(self,
             blog: str,
             client_key: str,
             client_secret: str,
             oauth_key: str,
             oauth_secret: str) -> None
```

Params:

- blog – The name of the blog (one you have auth for)
- client_key – AKA Consumer Key
- client_secret – AKA Consumer Secret
- oauth_key – AKA Token
- oauth_secret – AKA Token Secret

#### Posting

```
def post(self,
         *,
         content: Content],
         tags: Iterable[str] = tuple(),
         **kwargs) -> Mapping
```

Params:

- content – A content object containing the post content
- tags – an optional list of tags
- **kwargs – any additional arguments to be passed as post data

Returns a JSON encoded response or raises an HTTPError if the request fails

#### Post Info

```
def get_post(self,
             post_id: str | int,
             blog: str | None = None) -> Mapping
```

Params:

- post_id – The ID of the post
- blog – The blog for the post – defaults to the blog given to the tumblr object

Returns a JSON encoded response or raises an HTTPError if the request fails

#### Reblogging

```
def reblog(self,
           *,
           from_id: str | int,
           from_blog: str,
           content: list[Mapping],
           tags: Iterable[str] = tuple()) -> Mapping
```

Params:

- from_id – The ID of the post to be reblogged from
- from_blog – The blog of the post to be reblogged from
- content – A list of content block type Mappings
- tags – an optional list of tags

Returns a JSON encoded response or raises an HTTPError if the request fails

#### Poll Results

```
def poll_results(self,
                 post_id: str | int,
                 poll_id: str
                 blog: str | None = None) -> Mapping[str, Any]
```

Returns a result that contains a mapping of poll answer client_ids to the votes
for that answer (under the key "results").
Use the `utils.zip_poll_with_results` function to combine this with the poll
data.
Use the `utils.get_polls_from_post` function to get the poll data (which
contains the poll ID) from a post.

Params:

- post_id – The post that contains the poll
- poll_id – AKA the poll client_id
- blog – The blog for the post – defaults to the blog given to the tumblr object

Returns a JSON encoded response or raises an HTTPError if the request fails

### `Content`

Supports the creation of text post content with method chaining. Handles image
files, layout, and content blocks.

Contains the following functions:

- `poll`
- `ordered_list`
- `unordered_list`
- `image`
- `read_more`
- `row_of`
- `text`
- `heading`
- `subheading`
- `cursive`
- `quote`
- `indented`
- `chat`
- `ordered_list_item`
- `unordered_list_item`

All post types from `text` onward roughly translate to:

```
def <text_subtype>(self, content: str, **kwargs) -> Self:
    ...  # snip
    data = {
        "type": "text",
        "subtype": "<text_subtype>",
        "text": content,
        **kwargs,
    }
    ...  # snip
    return self
```

The other block types will be explained below.

#### `ordered_list`, and `unordered_list`

Each takes varargs of strings and adds a list of `ordered_list_item`s
or `unordered_list_item`s to the content respectively.

#### `poll`

```
def poll(self
         question: str,
         options: list[str],
         *,
         expire_after=timedelta(days=7),
         poll_uuid: UUID = None,
         option_uuids: list[UUID] = None) -> Self:
```

Adds a poll content block to the content. This is not officially documented so
may be unstable.

Params:

- question – The Poll prompt
- options – The poll options
- expire_after – a time delta of when the poll will close
- poll_uuid – an optional UUID4 – one will be generated if not given
- option_uuids – an optional list of UUID4s – a list will be generated if not
  given. Raises a Value error if the number of options does not match the number
  of given option UUIDs

Raises a ValueError if the option_uuids are given does not match the number of
options.

#### `read_more`

Inserts a truncating "read more" block into the post.

#### `image`

```
def image(self,
          path: PurePath | str,
          img_type: str,
          alt_text: str,
          caption: str | None = None) -> Self
```

Inserts an image into the text post. The image type is the images corresponding
MIME type.

#### `row_of`

Takes varargs of image data. image data can either be a mapping of image param
names to values, or an iterable of the image params.

### `tumblr.utils`

#### Poll Info

```
def get_polls_from_post(post_id: Any) -> Iterator[Mapping[str, Any]]
```

Params:

- post_id – The post that contains the poll

Returns an iterator of the poll block mappings contained in the post

This function returns an iterator as, try as tumblr might, it seems multiple
polls can be added to posts.

#### Zip Polls with Poll Results

```
def zip_poll_with_results(poll: Mapping[str, Any],
                          results: Mapping[str, Any]) -> Mapping[str, Any]
```

Utility function that combines poll data with the poll results.
Returns a new mapping with a "total_votes" key mapping to the total number of
votes and each poll answer has a "votes" key mapping to the number of votes for
that answer.

Params:

- poll – the poll block data
- results – the result data (either the response or response data)

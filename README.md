# Tumblr-Dot-Com

An unofficial Tumblr API client.
Includes support for creating polls and retrieving poll results.

## Install

```
pip install tumblrdotcom
```

## Docs

https://tumblr-dot-com.rtfd.io

## Usage

### Example

```python
import os
from datetime import timedelta
from pprint import pprint

from tumblr import *

tumblr = Blog(
    blog="pizza",  # or 'pizza.tumblr.com'
    client_key=os.getenv("CONSUMER_KEY"),
    client_secret=os.getenv("CONSUMER_SECRET"),
    oauth_key=os.getenv("OAUTH_TOKEN"),
    oauth_secret=os.getenv("OAUTH_SECRET"),
)

response = tumblr.post(
    content=(
        Heading("Hello, World!"),
        Text("Oh boy! Isn't it great to have a tumblr!"),
        Row(
            Image(
                "clown_left.jpg",
                "image/jpeg",
                "A photo clown holding their right thumb up towards the camera"
            ),
            Image(
                "clown_right.jpg",
                "image/jpeg",
                "A photo clown holding their left thumb up towards the camera"
            ),
        ),
        Poll(
            "Don't you think so?",
            ["Yes", "No"],
            expire_after=timedelta(days=1),
        ),
    ),
    tags=["pizza", "I can't even remember why they were deleted"],
)

pprint(response)
```

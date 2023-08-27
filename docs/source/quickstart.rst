Quickstart
==========

Nyaa~! Welcome to the Kawaii tumblr-dot-com API Client documentation!
This is, like, the most adorbs way to interact with Tumblr's API. Nya~! 😺

Install
-------

::

    pip install tumblrdotcom

You will also need to generate Oauth1 access tokens. See the
`Tumblr API documentation <https://www.tumblr.com/docs/en/api/v2#authentication>`_
for more.

Usage
-----

tumblrdotcom provides a :class:`~tumblr.Tumblr` class that manages getting
and retrieving posts and reblogs. :class:`~tumblr.Tumblr` objects are
initialised with the current user blog, and Oauth1 tokens, for example using
`python-dotenv <https://pypi.org/project/python-dotenv/>`_:

::

    import os
    
    from dotenv import load_dotenv
    from tumblr import *

    load_dotenv()

    tumblr = Tumblr(
        blog="staff",  # or "staff.tumblr.com" – use the blog you want to post from
        client_key=os.getenv("CONSUMER_KEY"),
        client_secret=os.getenv("CONSUMER_SECRET"),
        oauth_key=os.getenv("OAUTH_TOKEN"),
        oauth_secret=os.getenv("OAUTH_SECRET"),
    )

Posts or reblogs can be constructed with several content blocks. There are
several types of content blocks all defined in the :mod:`~tumblr.content`
module. For example:

::

    res = tumblr.post(
        content=(
            Heading("Making Posts on Tumblr"),
            Text("It's something to do."),
            Poll(
                question="What do you think?",
                options=[
                    "I agree with this",
                    "I do NOT agree with this",
                    "My thoughts on this are complex",
                ],
            ),
        ),
        tags=["thoughts", "tumbler"]
    )

    post_id = res["response"]["id"]

Here, content is given as a tuple of content blocks.

This post can then be retrieved using its ID (this is also used in the url to
the post):

::

    res = tumblr.get_post(post_id)

This post could also be reblogged:

::

    res = tumblr.reblog(
        from_id=post_id,
        from_blog="staff",
        content=(Text("I think this post is a little too controversial"),),
        tags=["drama"]
    )

The poll results can also be obtained:

::

    from pprint import pprint

    res = tumblr.poll_results(post_id)

    pprint(res["answers"])

Would produce something like:

::

    [{'answer_text': 'I agree with this',
      'client_id': 'b5efe07b-94f4-4a96-b8c8-9e4175aa5035',
      'votes': 123},
     {'answer_text': 'I do NOT agree with this',
      'client_id': '175a5d27-ebf8-44df-a2b2-9e16dff722de',
      'votes': 8},
     {'answer_text': 'My thoughts on this are complex',
      'client_id': 'f26e1d84-8740-42ef-90b4-d0026627ad24',
      'votes': 987}]

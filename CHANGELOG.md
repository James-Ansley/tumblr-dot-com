# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0]

### Breaking Changes

In a minor bump? Yes. Because tumblr changed how the Polls API works

- `Content.poll` no longer takes `option_uuids` or `poll_uuid` parameters. While
  these are still required in the request, they seem to be ignored and
  regenerated serverside.
- The `Content.poll` `expire_after` parameter is now clamped between 1 and 7
  days serverside.
- Only one `Content.poll` block can be added per post. However, polls can still
  be added to reblogs even if the post being reblogged contains a poll.

[0.1.0]: https://github.com/James-Ansley/tumblr-dot-com/compare/v0.0.1...v0.1.0

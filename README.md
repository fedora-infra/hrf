# hrf (Human Readable Fedmsg)

hrf is a tiny Flask application that accepts JSON blobs from the fedmsg bus
via `POST` requests and converts them into human readable strings that can be
used to display the information.

hrf takes JSON data in a POST request. It can take either a single JSON object
or a list of JSON objects.

In both cases it will return a JSON object back, which contains one entry:
`results`, which itself contains a list.

If you pass a single JSON object, the `results` list will, obviously, only
contain one element -- but **a list is always returned.** This is intentional
and done for consistency, so that apps using hrf don't have to special-case.

The list you get back in `results` will match the order of the JSON list you
provided, if you provided one.

You can POST to `/all` in the same way, except that then `results` will be
a list of **objects**, which is useful if you need multiple bits of
information at once.

**Noteworthy (for users):**

Generally, if you need data for multiple messages, try to POST as much as you
can at a time, because making a new HTTP connection to the app is expensive
(for your app). You will create a much better and faster UX by doing this.
Do not spawn a new connection to the app for each message in a batch, for
example. Turn them into a JSON list and send that. It is to your benefit.

Also, try to gzip your data where possible, for another speedup.

# Tests

Run tests with: `PYTHONPATH=$(pwd)/hrf python tests/tests.py`

# License

LGPL v2.1, same as fedmsg itself.

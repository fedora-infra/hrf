from flask import Flask, Response, request, jsonify
import fedmsg.config
import fedmsg.meta
import json
import datetime
import pretty
import requests
from pytz import timezone, UnknownTimeZoneError

meta_config = fedmsg.config.load_config([], None)
fedmsg.meta.make_processors(**meta_config)

app = Flask(__name__)
app.debug = True


def _timestamp(message, user_timezone):
    '''Return a dict containing the timestamp in a bunch of formats.'''
    ts = message['timestamp']
    ts_obj = datetime.datetime.fromtimestamp(ts)
    utc = timezone('UTC')
    utc_obj = utc.normalize(utc.localize(ts_obj))
    localized = utc_obj.astimezone(timezone(user_timezone))

    return {
        'ago': pretty.date(ts_obj),
        'iso': localized.isoformat(),
        'usadate': localized.strftime("%m/%d/%Y"),
        'fulldate': localized.strftime("%A, %B %d, %Y"),
        'time': localized.strftime("%H:%M"),
        'epoch': str(ts),
    }

meta_methods = {
    #'avatars': fedmsg.meta.msg2avatars,
    #'emails': fedmsg.meta.msg2emails,
    'icon': fedmsg.meta.msg2icon,
    'link': fedmsg.meta.msg2link,
    'objects': fedmsg.meta.msg2objects,
    'packages': fedmsg.meta.msg2packages,
    'repr': fedmsg.meta.msg2repr,
    'secondary_icon': fedmsg.meta.msg2secondary_icon,
    'subtitle': fedmsg.meta.msg2subtitle,
    'title': fedmsg.meta.msg2title,
    'usernames': fedmsg.meta.msg2usernames,
    'timestamp': _timestamp,
    'all': str,
}


@app.route("/")
def usage():
    methods = '\n'.join([
        '/' + name
        for name in sorted(meta_methods.keys())
    ])
    return Response(
        """Welcome to hrf - the Human Readable frontend to Fedmsg.

To use hrf, simply POST a list of fedmsg messages from datagrepper to any of the
endpoints below.

The names of the endpoints reflect the names of the fedmsg.meta API
methods. For example POSTing to /title will return fedmsg.meta.msg2title()
and POSTing to /repr will return fedmsg.meta.msg2repr().

If you 'GET' instead, we will query datagrepper on your behalf, sending it your
querystring.

Available endpoints:
%s
""" % methods,
        mimetype='text/plain')


@app.route("/<api_method>", methods=['POST', 'GET'])
def route(api_method):
    parsed = {}

    if request.method == 'GET':
        qs = request.query_string
        r = requests.get('https://apps.fedoraproject.org/datagrepper/raw/?' + qs)
        if r.status_code != 200:
            return jsonify({"error": "Datagrepper returned non-200 response code."}), 400
        else:
            parsed = r.json()['raw_messages']
    else:
        parsed = json.loads(request.data)

    user_timezone = request.args.get('timezone', 'UTC')

    # Sigh.
    if isinstance(parsed, dict):
        parsed = [parsed]

    results = []

    try:
        if api_method not in meta_methods:
            return jsonify({"error": "That method was invalid."}), 404

        for message in parsed:
            if api_method == 'all':
                # Return a JSON dict of all HR responses
                values = {}
                for name in meta_methods.keys():
                    if name == 'all':
                        continue
                    elif name == 'timestamp':
                        result = meta_methods[name](message, user_timezone)
                    else:
                        result = meta_methods[name](message)
                    if isinstance(result, set):
                        result = list(result)
                    values[name] = result
                results.append(values)
            elif api_method == 'timestamp':
                method = meta_methods[api_method]
                results.append(method(message, user_timezone))
            else:
                method = meta_methods[api_method]
                results.append(method(message))
    except UnknownTimeZoneError as e:
        return jsonify({"error": "Invalid timezone parameter."}), 400
    else:
        return jsonify({'results': results})


if __name__ == "__main__":
    app.run()

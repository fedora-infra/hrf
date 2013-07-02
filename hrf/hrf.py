from flask import Flask, Response, request, jsonify
import fedmsg.config
import fedmsg.meta
import json

meta_config = fedmsg.config.load_config([], None)
fedmsg.meta.make_processors(**meta_config)

app = Flask(__name__)
app.debug = True

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
    'all': str,
}

@app.route("/")
def usage():
    methods = '\n'.join(['POST /' + name for name in sorted(meta_methods.keys())])
    return Response(
        """Welcome to hrf - the Human Readable frontend to Fedmsg.

To use hrf, simply POST to any of the endpoints below.
The names of the endpoints reflect the names of the fedmsg.meta API
methods. For example POSTing to /title will return fedmsg.meta.msg2title()
and POSTing to /repr will return fedmsg.meta.msg2repr().

Available endpoints:
%s
""" % methods,
        mimetype='text/plain')

@app.route("/<api_method>", methods=['POST'])
def route(api_method):
    parsed = json.loads(request.data)

    # Sigh.
    if isinstance(parsed, dict):
        parsed = [parsed]

    results = []

    if api_method in meta_methods.keys():
        for message in parsed:
            if api_method == 'all':
                # Return a JSON dict of all HR responses
                values = {}
                for name in meta_methods.keys():
                    if name == 'all':
                        continue
                    result = meta_methods[name](message)
                    if isinstance(result, set):
                        result = list(result)
                    values[name] = result
                results.append(values)
            else:
                # This is guaranteed to exist at this point.
                method = meta_methods[api_method]
                results.append(method(message))

        return jsonify({'results': results})
    else:
        return "That method was invalid.", 404

if __name__ == "__main__":
    app.run()

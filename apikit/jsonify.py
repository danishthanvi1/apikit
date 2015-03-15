import json
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from flask import Response, request


class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def __init__(self, refs=False):
        self.refs = refs
        super(JSONEncoder, self).__init__()

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if self.refs and hasattr(obj, 'to_ref'):
            return obj.to_ref()
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        try:
            from bson.objectid import ObjectId
            if isinstance(obj, ObjectId):
                return str(obj)
        except ImportError:
            pass
        return json.JSONEncoder.default(self, obj)


def jsonify(obj, status=200, headers=None, refs=False, encoder=JSONEncoder):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    if encoder is JSONEncoder:
        data = encoder(refs=refs).encode(obj)
    else:
        data = encoder().encode(obj)
    if 'callback' in request.args:
        cb = request.args.get('callback')
        data = '%s && %s(%s)' % (cb, cb, data)
    return Response(data, headers=headers,
                    status=status,
                    mimetype='application/json')
def add_from_scope(scope, *args, **kw):
    scope.get('event').append(EventFrame(*args, **kw))


class EventFrame(object):
    pass

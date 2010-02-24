
class ResponseStatusError(Exception):
    def __init__(self, error):
        Exception.__init__(self, "ResponseStatusError: %s" % error)

class InvalidObjectType(Exception):
    def __init__(self, error):
        Exception.__init__(self, "InvalidObjectType: %s" % error)

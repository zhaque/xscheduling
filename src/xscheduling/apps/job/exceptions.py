class NoInitialData(Exception):
    def __init__(self, error):
        Exception.__init__(self, "NoInitailData: %s" % error)

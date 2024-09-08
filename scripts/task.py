class Task():
    def __init__(self, type, subtype=None, callback=None, *args, **kwargs):
        self.type = type
        self.subtype = subtype
        self.callback = callback
        self.data = kwargs.get('data')
        self.args = args
        self.kwargs = kwargs
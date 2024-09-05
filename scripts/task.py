class Task():
    def __init__(self, type, callback=None, *args, **kwargs):
        self.type = type
        self.subtype = kwargs.get('subtype')
        self.callback = callback
        self.data = kwargs.get('data')
        self.args = args
        self.kwargs = kwargs
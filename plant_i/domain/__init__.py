def init_once(cls):
    if getattr(cls, "__static_init__", None):
        cls.__static_init__()
    return cls


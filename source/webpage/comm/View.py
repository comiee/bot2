from webpage.mei.urls import add_url
from abc import abstractmethod


class _ViewMeta(type):
    def __init__(cls: 'View', name, bases, attrs, **kwargs):  # 定义新类的时候执行
        super().__init__(name, bases, attrs, **kwargs)
        if name != 'View':
            add_url(cls.url, cls.handle)


class View(metaclass=_ViewMeta):
    url: str

    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def handle(cls, request):
        instance = cls.get_instance()
        if request.POST:
            return instance.post(request)
        return instance.get(request)

    @abstractmethod
    def post(self, request):
        pass

    def get(self, request):
        return self.post(request)

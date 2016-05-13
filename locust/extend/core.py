# -*- coding: utf-8 -*-

from .clients import JsonRpcSession
from locust.core import Locust
from locust.exception import LocustError


class JsonRpcLocust(Locust):
    client = None

    def __init__(self):
        super(JsonRpcLocust, self).__init__()

        if self.host is None:
            raise LocustError(
                "You must specify the base host. Either in the host attribute in the Locust class, or on the command "
                "line using the --host option.")

        self.client = JsonRpcSession(base_url=self.host)

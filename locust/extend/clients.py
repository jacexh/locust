# -*- coding: utf-8 -*-

import time
try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json
from locust import events
from locust.clients import HttpSession, ResponseContextManager
from requests.exceptions import RequestException


class JsonRpcSession(HttpSession):

    def request(self, method, url, name=None, catch_response=False, **kwargs):
        """

        :param method:
        :param url:
        :param name:
        :param catch_response:
        :param kwargs:
        :return:
        """
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)

        # store meta data that is used when reporting the request to locust's statistics
        # set up pre_request hook for attaching meta data to the request object
        request_meta = {"method": "jsonrpc", "start_time": time.time()}

        response = self._send_request_safe_mode(method, url, **kwargs)

        # record the consumed time
        request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)

        # get json-rpc method name from payload
        payload = kwargs.get('json', None) or kwargs['data']
        if payload and (not isinstance(payload, dict)):
            payload = json.loads(payload)
        method_name = payload['method']
        endpoint = (response.history and response.history[0] or response).request.path_url

        request_meta["name"] = name or endpoint + "::" + method_name

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        request_meta["content_size"] = len(response.content or "")

        if catch_response:
            response.locust_request_meta = request_meta
            return ResponseContextManager(response)
        else:
            try:
                response.raise_for_status()
            except RequestException as e:
                events.request_failure.fire(
                    request_type=request_meta["method"],
                    name=request_meta["name"],
                    response_time=request_meta["response_time"],
                    exception=e,
                )
            else:
                to_dict = response.json()
                if to_dict.get('error', None):
                    events.request_failure.fire(
                        request_type=request_meta['method'],
                        name=request_meta['name'],
                        response_time=request_meta['response_time'],
                        exception=to_dict['error'].get('message', 'unknown error')
                    )
                else:
                    events.request_success.fire(
                        request_type=request_meta["method"],
                        name=request_meta["name"],
                        response_time=request_meta["response_time"],
                        response_length=request_meta["content_size"],
                    )
            return response

from tornado.web import Application, RequestHandler
from tornado.testing import AsyncHTTPTestCase

from tornado_restplus import Api

class ApiLazyLoadingTest(AsyncHTTPTestCase):
    def get_app(self):
        # AsyncHTTPTestCase keeps application under self._app
        # but in order to keep convention and not touch _prefixed
        # variables, lets store it under self.app in ordef to use it later
        # for api initialization
        self.app = Application()
        return self.app

    def test_lazy_loading(self):
        api = Api()
        ns = api.namespace('TestNamespace')

        @ns.route('/first_handler', reply='[0]')
        class SomeFirstHandler(RequestHandler):
            def initialize(self, reply):
                self.reply = reply

            def get(self):
                self.write(self.reply)

        api.init_app(self.app)
        response = self.fetch('/TestNamespace/first_handler')
        assert response.code == 200
        assert response.body == b'[0]'

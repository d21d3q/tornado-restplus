from tornado.web import RequestHandler


class BaseEchoHandler(RequestHandler):
    def initialize(self, reply):
        self.reply = reply

    def get(self):
        # Lets include class name in response so that we can be
        # sure that we have response from specific handler
        self.write('{} {}'.format(self.__class__.__name__, self.reply))

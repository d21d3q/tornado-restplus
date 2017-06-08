import logging
from apispec import APISpec

from .namespace import Namespace

log = logging.getLogger(__name__)


class Api(object):
    def __init__(self, app=None, version='1.0', title=None, description=None,
                 terms_url=None, license=None, license_url=None,
                 contact=None, contact_url=None, contact_email=None,
                 authorizations=None, security=None, doc='/',
                 default='default',  # default_id=default_id,
                 default_label='Default namespace', validate=None,
                 tags=None,
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=False, serve_challenge_on_401=False,
                 format_checker=None,
                 **kwargs):
        self.version = version
        self.title = title or 'API'
        self.description = description
        self.terms_url = terms_url
        self.contact = contact
        self.contact_email = contact_email
        self.contact_url = contact_url
        self.license = license
        self.license_url = license_url
        self.authorizations = authorizations
        # self.security = security
        # self.default_id = default_id
        self._validate = validate
        self._doc = doc
        self._doc_view = None
        self._default_error_handler = None
        self.tags = tags or []

        # self.error_handlers = {
        #     ParseError: mask_parse_error_handler,
        #     MaskError: mask_error_handler,
        # }
        self._schema = None
        self.models = {}
        self._refresolver = None
        self.format_checker = format_checker
        self.namespaces = []
        self.default_namespace = self.namespace(default, default_label,
                                                endpoint='{0}-declaration'
                                                .format(default),
                                                validate=validate,
                                                api=self,
                                                path='/')
        self.ns_paths = dict()
        self.spec = APISpec(title, version, plugins=['apispec.ext.tornado'])
        # self.representations = OrderedDict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        # self.default_mediatype = default_mediatype
        # self.decorators = decorators if decorators else []
        # self.catch_all_404s = catch_all_404s
        # self.serve_challenge_on_401 = serve_challenge_on_401
        # self.blueprint_setup = None
        self.endpoints = set()
        self.resources = []
        self.app = None
        # self.blueprint = None

        if app is not None:
            self.app = app
            self.init_app(app)

    def init_app(self, app, **kwargs):
        '''
        Allow to lazy register the API on a tornado application::

        >>> app = tornado.Application(__name__)
        >>> api = Api()
        >>> api.init_app(app)

        :param tornado.Application app: the Tornado application object
        :param str title: The API title (used in Swagger documentation)
        :param str description: The API description (used in Swagger
                                documentation)
        :param str terms_url: The API terms page URL (used in Swagger
                              documentation)
        :param str contact: A contact email for the API (used in Swagger
                            documentation)
        :param str license: The license associated to the API (used in Swagger
                            documentation)
        :param str license_url: The license page URL (used in Swagger
                                documentation)

        '''
        self.title = kwargs.get('title', self.title)
        self.description = kwargs.get('description', self.description)
        self.terms_url = kwargs.get('terms_url', self.terms_url)
        self.contact = kwargs.get('contact', self.contact)
        self.contact_url = kwargs.get('contact_url', self.contact_url)
        self.contact_email = kwargs.get('contact_email', self.contact_email)
        self.license = kwargs.get('license', self.license)
        self.license_url = kwargs.get('license_url', self.license_url)
        self._add_specs = kwargs.get('add_specs', True)

        self._init_app(app)

    def _init_app(self, app):
        '''
        Perform initialization actions with the given
        :class:`tornado.Application` object.

        :param tornado.Application app: The tornado application object
        '''

        if len(self.resources) > 0:
            self._register_view(app, self.resources)

    def get_ns_path(self, ns):
        return self.ns_paths.get(ns)

    def ns_urls(self, ns, urls):
        path = self.get_ns_path(ns) or ns.path
        return [path + url for url in urls]

    def add_namespace(self, ns, path=None):
        '''
        This method registers resources from namespace for current instance of
        api. You can use argument path for definition custom prefix url for
        namespace.

        :param Namespace ns: the namespace
        :param path: registration prefix of namespace
        '''
        if ns not in self.namespaces:
            self.namespaces.append(ns)
            if self not in ns.apis:
                ns.apis.append(self)
            # Associate ns with prefix-path
            if path is not None:
                self.ns_paths[ns] = path
        # Register resources
        for resource, urls, kwargs in ns.resources:
            self.register_resource(ns, resource, *self.ns_urls(ns, urls),
                                   **kwargs)

    def namespace(self, *args, **kwargs):
        '''
        A namespace factory.

        :returns Namespace: a new namespace instance
        '''
        ns = Namespace(*args, **kwargs)
        self.add_namespace(ns)
        return ns

    def register_resource(self, namespace, resource, *urls, **kwargs):
        urlspecs = []
        for url in urls:
            urlspecs.append((url, resource, kwargs))

        if self.app is not None:
            self._register_view(self.app, urlspecs)
        else:
            self.resources.extend(urlspecs)
        return urlspecs

    def _register_view(self, app, urlspecs):
        app.add_handlers(r'.*', urlspecs)

from tornado.web import Application
from unittest import TestCase

from tornado_restplus import Api
from tests.common import BaseEchoHandler
from marshmallow import Schema, fields


class SpecTest(TestCase):
    def setUp(self):
        super(SpecTest, self).setUp()
        self.app = Application()
        self.api = Api(self.app, title='Api title')
        self.ns = self.api.namespace('api')

    def test_route_spec(self):

        @self.ns.route('/path', _doc=True)
        class SomeHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                '''
                pass

            def post():
                pass

        @self.ns.route('/another_path', _doc=True)
        class AnotherHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting from another handler
                responses:
                    200:
                        description: A greeting to the client from another
                                     handler
                '''
                pass

        doc = self.api.spec.to_dict()
        assert doc['info']['title'] == 'Api title'
        assert '/api/path' in doc['paths']
        assert doc['paths']['/api/path']['get']['description'] == \
            'Get a greeting'
        assert '/api/another_path' in doc['paths']
        assert doc['paths']['/api/another_path']['get']['description'] == \
            'Get a greeting from another handler'

    def test_route_without_spec(self):
        @self.ns.route('/path', _doc=False)
        class SomeHandler(BaseEchoHandler):
            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                '''
                pass

            def post():
                pass

        doc = self.api.spec.to_dict()
        assert doc['info']['title'] == 'Api title'
        assert '/api/path' not in doc['paths']

    def test_schema_definition_in_registered_namespace(self):
        class CategorySchema(Schema):
            id = fields.Int()
            name = fields.Str(required=True)

        class PetSchema(Schema):
            category = fields.Nested(CategorySchema, many=True)
            name = fields.Str()

        @self.ns.route('/path', _doc=True)
        class SomeHandler(BaseEchoHandler):

            def get(self):
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                        schema: PetSchema
                '''
                pass

            def post(self):
                pass

        self.ns.definition('Category', schema=CategorySchema)
        self.ns.definition('Pet', schema=PetSchema)
        doc = self.api.spec.to_dict()
        assert len(doc['definitions']) == 2
        assert 'Category' in doc['definitions']
        assert 'name' in doc['definitions']['Category']['properties']
        assert 'id' in doc['definitions']['Category']['properties']
        assert 'Pet' in doc['definitions']
        assert 'name' in doc['definitions']['Pet']['properties']
        assert 'category' in doc['definitions']['Pet']['properties']

    def test_schema_definition_in_api(self):
        class CategorySchema(Schema):
            id = fields.Int()
            name = fields.Str(required=True)

        class PetSchema(Schema):
            category = fields.Nested(CategorySchema, many=True)
            name = fields.Str()

        @self.ns.route('/path', _doc=True)
        class SomeHandler(BaseEchoHandler):

            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                        schema: PetSchema
                '''
                pass

            def post():
                pass

        self.api.definition('Category', schema=CategorySchema)
        self.api.definition('Pet', schema=PetSchema)
        doc = self.api.spec.to_dict()
        assert len(doc['definitions']) == 2
        assert 'Category' in doc['definitions']
        assert 'name' in doc['definitions']['Category']['properties']
        assert 'id' in doc['definitions']['Category']['properties']
        assert 'Pet' in doc['definitions']
        assert 'name' in doc['definitions']['Pet']['properties']
        assert 'category' in doc['definitions']['Pet']['properties']

    def test_schema_definition_lazy_loading(self):
        class CategorySchema(Schema):
            id = fields.Int()
            name = fields.Str(required=True)

        class PetSchema(Schema):
            category = fields.Nested(CategorySchema, many=True)
            name = fields.Str()

        @self.ns.route('/path', _doc=True)
        class SomeHandler(BaseEchoHandler):

            def get():
                '''Get a greeting endpoint.
                ---
                description: Get a greeting
                responses:
                    200:
                        description: A greeting to the client
                        schema: PetSchema
                '''
                pass

            def post():
                pass

        ns = self.api.namespace('lazy_api')
        ns.definition('Category', schema=CategorySchema)
        ns.definition('Pet', schema=PetSchema)
        self.api.add_namespace(ns)
        doc = self.api.spec.to_dict()
        assert len(doc['definitions']) == 2
        assert 'Category' in doc['definitions']
        assert 'name' in doc['definitions']['Category']['properties']
        assert 'id' in doc['definitions']['Category']['properties']
        assert 'Pet' in doc['definitions']
        assert 'name' in doc['definitions']['Pet']['properties']
        assert 'category' in doc['definitions']['Pet']['properties']

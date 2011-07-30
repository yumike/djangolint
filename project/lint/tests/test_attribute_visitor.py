import ast
from django.test import TestCase
from ..analyzers.base import AttributeVisitor


class AttributeVisitorTests(TestCase):

    def get_attribute_node(self, source):
        return ast.parse(source).body[0].value

    def test_usable(self):
        visitor = AttributeVisitor()
        visitor.visit(self.get_attribute_node('foo.bar.baz'))
        self.assertEqual(visitor.is_usable, True)
        self.assertEqual(visitor.get_name(), 'foo.bar.baz')

    def test_unusable(self):
        visitor = AttributeVisitor()
        visitor.visit(self.get_attribute_node('(foo or bar).baz'))
        self.assertEqual(visitor.is_usable, False)

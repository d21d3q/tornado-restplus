from unittest import TestCase
from tornado_restplus.utils import make_path_chunk


class UtilsTest(TestCase):
    def test_make_path_chunk(self):
        valid = '/chunk'
        assert make_path_chunk('/chunk') == valid
        assert make_path_chunk('chunk') == valid
        assert make_path_chunk('//chunk') == valid
        assert make_path_chunk('///chunk') == valid
        assert make_path_chunk('/chunk//') == valid
        assert make_path_chunk('/chunk//') == valid
        assert make_path_chunk('chunk/') == valid
        assert make_path_chunk('chunk//') == valid
        assert make_path_chunk('chunk///') == valid

        valid = '/double/chunk'
        assert make_path_chunk('/double/chunk') == valid
        assert make_path_chunk('//double/chunk') == valid
        assert make_path_chunk('/double/chunk//') == valid

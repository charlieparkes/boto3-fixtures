import os

from boto3_fixtures import utils


def test_batch():
    things = [1, 2, 3, 4, 5, 6]
    iter = list(utils.batch(things, 2))
    assert len(iter) == 3
    assert iter[0] == [1, 2]
    assert iter[1] == [3, 4]
    assert iter[2] == [5, 6]


class TestEnviron:
    def test_set(self):
        key = "BOTO3_FIXTURES_TEST"
        assert os.getenv(key, None) is None
        with utils.set_env({key: "foobar"}):
            assert os.getenv(key, None) == "foobar"
        assert os.getenv(key, None) is None

    def test_set_existing_verwrite(self):
        key = "BOTO3_FIXTURES_TEST"
        os.environ[key] = "wizbang"
        assert os.getenv(key, None) == "wizbang"
        with utils.set_env({key: "foobar"}):
            assert os.getenv(key, None) == "foobar"
        assert os.getenv(key, None) == "wizbang"

    def test_set_existing_no_overwrite(self):
        key = "BOTO3_FIXTURES_TEST"
        os.environ[key] = "wizbang"
        assert os.getenv(key, None) == "wizbang"
        with utils.set_env({key: "foobar"}, overwrite=False):
            assert os.getenv(key, None) == "wizbang"
        assert os.getenv(key, None) == "wizbang"


def test_repr():
    class FooBar:
        pass

    foo = FooBar()
    assert utils.repr(foo) == "FooBar()"


def test_e_to_str():
    try:
        raise Exception("foo bar")
    except Exception as e:
        assert utils.exception_to_str(e) == "Exception foo bar"

import json
import unittest
from unittest.mock import patch, MagicMock

import redis
from provider.cache import CacheClient, cached


class TestCacheClient(unittest.TestCase):
    def setUp(self):
        CacheClient._instance = None

    @patch("redis.Redis")
    def test_singleton_pattern(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        client1 = CacheClient()
        client2 = CacheClient()

        self.assertIs(
            client1, client2, "CacheClient deve implementar o padrão singleton"
        )
        mock_redis.assert_called_once()

    @patch("redis.Redis")
    def test_connection_error_handling(self, mock_redis):
        mock_redis.side_effect = redis.ConnectionError("Connection error")

        client = CacheClient()

        self.assertIsNone(client._redis)
        self.assertFalse(client.is_available())

    @patch("redis.Redis")
    def test_get_with_valid_key(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis_instance.get.return_value = json.dumps({"key": "value"})
        mock_redis.return_value = mock_redis_instance

        client = CacheClient()

        result = client.get("test_key")
        self.assertEqual(result, {"key": "value"})
        mock_redis_instance.get.assert_called_once_with("test_key")

    @patch("redis.Redis")
    def test_set_successful(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance

        client = CacheClient()

        result = client.set("test_key", {"key": "value"}, 3600)
        self.assertTrue(result)
        mock_redis_instance.setex.assert_called_once()


class TestCachedDecorator(unittest.TestCase):
    @patch("provider.cache.CacheClient")
    def test_cached_decorator_hit(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.get.return_value = "cached_value"
        mock_client_class.return_value = mock_client

        @cached(prefix="test")
        def test_function(arg1, arg2):
            return f"{arg1}_{arg2}"

        result = test_function("foo", "bar")
        self.assertEqual(result, "cached_value")
        mock_client.get.assert_called_once()
        mock_client.set.assert_not_called()

    @patch("provider.cache.CacheClient")
    def test_cached_decorator_miss(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.get.return_value = None
        mock_client_class.return_value = mock_client

        @cached(prefix="test")
        def test_function(arg1, arg2):
            return f"{arg1}_{arg2}"

        result = test_function("foo", "bar")
        self.assertEqual(result, "foo_bar")
        mock_client.get.assert_called_once()
        mock_client.set.assert_called_once()

    @patch("provider.cache.CacheClient")
    def test_cached_decorator_redis_unavailable(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.is_available.return_value = False
        mock_client_class.return_value = mock_client

        @cached(prefix="test")
        def test_function(arg1, arg2):
            return f"{arg1}_{arg2}"

        result = test_function("foo", "bar")
        self.assertEqual(result, "foo_bar")
        mock_client.get.assert_not_called()
        mock_client.set.assert_not_called()

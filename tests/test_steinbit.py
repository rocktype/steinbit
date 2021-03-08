import unittest
from steinbit.steinbit import Steinbit


class SteinbitTest(unittest.TestCase):

    def test_something(self):
        assert str(Steinbit()) == "Steinbit"

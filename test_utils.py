#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import unittest
from utils import database

class TestCron(unittest.TestCase):
    pass

class TestDatabase(unittest.TestCase):

    def test_create(self):
        database.create()

if __name__ == '__main__':
    unittest.main()
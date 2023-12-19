#!/glade/apps/opt/modulefiles/idep python
from __future__ import print_function

import unittest
from utils import cron, database

class TestCron(unittest.TestCase):
    pass

class TestDatabase(unittest.TestCase):

    def test_create(self):
        database.create()

    

if __name__ == '__main__':
    unittest.main()

#setUp()
    
#tearDown()
    
#setUpClass()
    
#tearDownClass()

# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# assertIs(a, b)
# assertIsNot(a, b)
# assertIsNone(x)
# assertIsNotNone(x)
# assertIn(a, b)
# assertNotIn(a, b)
# assertIsInstance(a, b)
# assertNotIsInstance(a, b)

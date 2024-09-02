import unittest

import src.query_validation as qv

class Test(unittest.TestCase):

    def test_correct_type(self):
        self.assertIsInstance(qv.validate_names(["lucas", "llort", "bonnefont"]), qv.ValidQuery)


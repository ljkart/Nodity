import unittest
from utils import node_finder


class TestMain(unittest.TestCase):
    """Test class"""
    def test_node_finder(self):
        """Basic Test"""
        data_dict = node_finder.get_node_list()
        self.assertTrue(data_dict)
        self.assertEqual(dict, type(data_dict))


if __name__ == "__main__":
    unittest.main()
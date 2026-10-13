import unittest
from tools.m118_validate_city_data import check
class M118CityData(unittest.TestCase):
 def test_user_grounded_counts_and_no_authorization(self):
  self.assertTrue(check())
if __name__=="__main__":unittest.main()

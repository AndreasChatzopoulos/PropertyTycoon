import unittest
from unittest.mock import MagicMock
from property import Property

class TestProperty(unittest.TestCase):
    def setUp(self):
        self.mock_owner = MagicMock()
        self.mock_owner.name = "Player1"
        self.mock_owner.owned_properties = []
        self.property1 = Property(1, "Mediterranean Avenue", 60, [2, 10, 30, 90, 160, 250], 50, "Brown")
        self.property2 = Property(3, "Baltic Avenue", 60, [4, 20, 60, 180, 320, 450], 50, "Brown")
        self.station = Property(5, "Reading Railroad", 200, [25, 50, 100, 200], 0, "Station")
        self.utility = Property(12, "Electric Company", 150, [], 0, "Utilities")

    # __init__ 
    def test_initialization(self):
        self.assertEqual(self.property1.name, "Mediterranean Avenue")
        self.assertEqual(self.property1.price, 60)
        self.assertEqual(self.property1.position, 1)
        self.assertEqual(self.property1.rent, [2, 10, 30, 90, 160, 250])
        self.assertEqual(self.property1.house_cost, 50)
        self.assertEqual(self.property1.group, "Brown")
        self.assertFalse(self.property1.completed)
        self.assertEqual(self.property1.houses, 0)
        self.assertIsNone(self.property1.owner)
        self.assertFalse(self.property1.mortgaged)

    # calculate_rent(self, dice_roll=0)
    def test_calculate_rent_with_full_set(self):
        self.property1.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.property1, self.property2]
        self.property1.completed = True
        self.assertEqual(self.property1.calculate_rent(), 4)  # Rent doubles
    
    def test_calculate_rent_with_houses(self):
        self.property1.houses = 3
        self.property1.owner = self.mock_owner
        self.assertEqual(self.property1.calculate_rent(), 90)

    def test_calculate_rent_station(self):
        self.station.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.station]
        self.assertEqual(self.station.calculate_rent(), 25)
    
    def test_calculate_rent_multiple_stations(self):
        station2 = Property(15, "Pennsylvania Railroad", 200, None, 0, "Station")
        self.station.owner = self.mock_owner
        station2.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.station, station2]
        self.assertEqual(self.station.calculate_rent(), 50)

    def test_calculate_rent_utilities_single(self):
        self.utility.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.utility]
        self.assertEqual(self.utility.calculate_rent(7), 28)
    
    def test_calculate_rent_utilities_both(self):
        utility2 = Property(28, "Water Works", 150, None, 0, "Utilities")
        self.utility.owner = self.mock_owner
        utility2.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.utility, utility2]
        self.assertEqual(self.utility.calculate_rent(7), 70)
    
    # transfer_property(self, new_owner)
    def test_transfer_property(self):
        new_owner = MagicMock()
        new_owner.name = "Player2"
        new_owner.owned_properties = []
        
        self.property1.transfer_property(new_owner)
        self.assertEqual(self.property1.owner, new_owner)
        self.assertIn(self.property1, new_owner.owned_properties)
    
    # check_completion(self)
    def test_check_completion(self):
        self.property1.owner = self.mock_owner
        self.property2.owner = self.mock_owner
        self.mock_owner.owned_properties = [self.property1, self.property2]
        self.assertTrue(self.property1.check_completion())
        self.assertTrue(self.property2.check_completion())

if __name__ == "__main__":
    unittest.main()

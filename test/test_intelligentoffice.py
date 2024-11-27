import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy(self, mock_infrared_sensor: Mock):
        mock_infrared_sensor.return_value = True
        system = IntelligentOffice()
        occupied = system.check_quadrant_occupancy(system.INFRARED_PIN1)
        self.assertTrue(occupied)

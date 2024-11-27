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

    def test_check_quadrant_occupancy_raises_error(self):
        system = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, system.check_quadrant_occupancy, -1)

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_open_at_8_am(self, mock_servo: Mock, mock_current_time: Mock):
        mock_current_time.return_value = datetime(2024,11,6,8,0)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_servo.assert_called_with(12)
        self.assertTrue(system.blinds_open)

    @patch.object(SDL_DS3231, "read_datetime")
    @patch.object(IntelligentOffice, "change_servo_angle")
    def test_manage_blinds_based_on_time_close_at_8_pm(self, mock_servo: Mock, mock_current_time: Mock):
        mock_current_time.return_value = datetime(2024,11,6,20,0)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        self.assertFalse(system.blinds_open)

    @patch.object(VEML7700, "lux")
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_on_light_if_lower_than_500_lux(self, mock_lightbulb: Mock, mock_ambient_light_sensor: Mock):
        mock_ambient_light_sensor.return_value = 499
        system = IntelligentOffice()
        system.manage_light_level()
        mock_lightbulb.assert_called_with(system.LED_PIN, True)
        self.assertTrue(system.light_on)
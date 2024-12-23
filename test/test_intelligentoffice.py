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

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_off_light_if_higher_than_550_lux(self, mock_lightbulb: Mock, mock_ambient_light_sensor: Mock):
        mock_ambient_light_sensor.return_value = 551
        system = IntelligentOffice()
        system.manage_light_level()
        mock_lightbulb.assert_called_with(system.LED_PIN, False)
        self.assertFalse(system.light_on)

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_manage_light_level_turn_off_light_if_all_quadrants_are_empty(self, mock_infrared_sensor: Mock, mock_lightbulb: Mock, mock_ambient_light_sensor: Mock):
        mock_ambient_light_sensor.return_value = 499
        mock_infrared_sensor.side_effect = [False, False, False, False]
        system = IntelligentOffice()
        system.manage_light_level()
        mock_lightbulb.assert_called_with(system.LED_PIN, False)
        self.assertFalse(system.light_on)

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_manage_light_level_turn_on_light_if_any_quadrant_is_occupied_and_lower_than_500_lux(self, mock_infrared_sensor: Mock, mock_lightbulb: Mock, mock_ambient_light_sensor: Mock):
        mock_ambient_light_sensor.return_value = 499
        mock_infrared_sensor.side_effect = [False, True, False, False]
        system = IntelligentOffice()
        system.manage_light_level()
        mock_lightbulb.assert_called_with(system.LED_PIN, True)
        self.assertTrue(system.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_monitor_air_quality_buzzer_turns_on_if_smoke_is_detected(self, mock_smoke_sensor: Mock, mock_buzzer: Mock):
        mock_smoke_sensor.return_value = False
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_with(system.BUZZER_PIN, True)
        self.assertTrue(system.buzzer_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_monitor_air_quality_buzzer_turns_off_if_smoke_is_not_detected(self, mock_smoke_sensor: Mock, mock_buzzer: Mock):
        mock_smoke_sensor.return_value = True
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_with(system.BUZZER_PIN, False)
        self.assertFalse(system.buzzer_on)
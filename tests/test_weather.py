from unittest.mock import patch, Mock

import pytest

from weather import get_weather

_MOCK_DATA = {
    "current_condition": [{"temp_C": "22", "weatherDesc": [{"value": "晴れ"}]}],
    "weather": [{
        "maxtempC": "28",
        "mintempC": "18",
        "hourly": [{"chanceofrain": "10"}, {"chanceofrain": "30"}, {"chanceofrain": "5"}],
    }],
}


def test_get_weather_returns_expected_fields():
    mock_resp = Mock()
    mock_resp.json.return_value = _MOCK_DATA

    with patch("weather.requests.get", return_value=mock_resp):
        result = get_weather()

    assert result == {
        "desc": "晴れ",
        "temp": "22",
        "temp_max": "28",
        "temp_min": "18",
        "precip_prob": 30,
        "url": "https://wttr.in/Nagoya",
    }


def test_get_weather_uses_max_precip():
    data = {
        "current_condition": [{"temp_C": "15", "weatherDesc": [{"value": "曇り"}]}],
        "weather": [{
            "maxtempC": "20",
            "mintempC": "10",
            "hourly": [{"chanceofrain": "50"}, {"chanceofrain": "80"}, {"chanceofrain": "20"}],
        }],
    }
    mock_resp = Mock()
    mock_resp.json.return_value = data

    with patch("weather.requests.get", return_value=mock_resp):
        result = get_weather()

    assert result["precip_prob"] == 80


def test_get_weather_raises_on_http_error():
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = Exception("HTTP 500")

    with patch("weather.requests.get", return_value=mock_resp):
        with pytest.raises(Exception):
            get_weather()

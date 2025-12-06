"""
Mock tool functions for demonstration purposes.
These simulate real API calls with deterministic/random responses.
"""

import random


def get_weather(location: str) -> str:
    """
    Get mock weather for any location.
    Uses first letter of location to deterministically select weather.
    """
    weather_options = ["sunny", "rainy", "windy", "cloudy", "blizzard", "sandstorm", "plague"]
    
    # Use first letter's ASCII value modulo length to pick weather
    first_letter = location[0].lower() if location else 'a'
    index = ord(first_letter) % len(weather_options)
    weather = weather_options[index]
    
    # Generate temperature based on weather
    temp_ranges = {
        "sunny": (70, 85),
        "rainy": (50, 65),
        "windy": (55, 70),
        "cloudy": (60, 75),
        "blizzard": (10, 32),
        "sandstorm": (85, 110),
        "plague": (65, 75)
    }
    
    temp_range = temp_ranges[weather]
    temp = random.randint(temp_range[0], temp_range[1])
    
    return f"Weather in {location}: {temp}°F, {weather}"


def get_flight_prices(origin: str, destination: str, date: str) -> str:
    """
    Get mock flight prices between two cities.
    Returns random price between $300 and $2000.
    """
    price = random.randint(300, 2000)
    return f"Flights from {origin} to {destination} on {date}: ${price}"


def get_currency_exchange(from_currency: str, to_currency: str, amount: float) -> str:
    """
    Get mock currency exchange rate.
    Returns random rate between 0.30 and 2.85.
    """
    rate = random.uniform(0.30, 2.85)
    result = amount * rate
    return f"{amount} {from_currency} = {result:.2f} {to_currency} (rate: {rate:.4f})"

def divide_by_secret_number(numerator: int) -> int:
	"""
	Divides by secret number.
	For demo purposes, forcing an error.
	"""
	return numerator / 0


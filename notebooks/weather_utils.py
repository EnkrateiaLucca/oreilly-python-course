# weather_utils.py

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def calculate_heat_index(temperature, humidity):
    """Calculate heat index based on temperature (°F) and humidity (%)"""
    if temperature < 80:
        return temperature
    
    heat_index = -42.379 + 2.04901523 * temperature + 10.14333127 * humidity
    heat_index -= 0.22475541 * temperature * humidity
    heat_index -= 6.83783e-3 * temperature**2
    heat_index -= 5.481717e-2 * humidity**2
    heat_index += 1.22874e-3 * temperature**2 * humidity
    heat_index += 8.5282e-4 * temperature * humidity**2
    heat_index -= 1.99e-6 * temperature**2 * humidity**2
    
    return round(heat_index, 2)
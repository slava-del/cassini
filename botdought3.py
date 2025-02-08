import os
import telebot
import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from telebot import types

# Load environment variables
load_dotenv()

# Retrieve tokens from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Replace 'BOT_TOKEN' in .env with your bot token key
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')  # Replace 'WEATHER_TOKEN' in .env with your OpenWeather token key

# Ensure tokens are set
if not BOT_TOKEN or not WEATHER_TOKEN:
    raise ValueError("Environment variables BOT_TOKEN or WEATHER_TOKEN are missing. Please check your .env file.")

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store user data in memory (for simplicity)
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Sends a welcome message with buttons when the '/start' command is issued.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Weather")
    item2 = types.KeyboardButton("Help")
    markup.add(item1, item2)

    bot.send_message(
        message.chat.id,
        "Hello! What would you like to search for?",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.lower() == "weather")
def prompt_location_for_weather(message):
    """
    Prompts the user for a location when the 'Weather' button is pressed.
    """
    location_prompt = 'Please type a location (city name or coordinates) for weather information: '
    sent_message = bot.send_message(message.chat.id, location_prompt)
    bot.register_next_step_handler(sent_message, fetch_weather)

@bot.message_handler(func=lambda message: message.text.lower() == "help")
def send_help(message):
    """
    Sends a help message when the 'Help' button is pressed.
    """
    help_message = (
        "Here are some commands you can use:\n"
        "weather - Get weather information\n"
        "air_quality - Get air quality index\n"
        "weather_map - Get weather maps\n"
        "Simply type a location after choosing an option.\n"
        "Enjoy using the bot!"
    )
    bot.send_message(message.chat.id, help_message)

def location_handler(location_name):
    """
    Uses the Nominatim geocoder to get latitude and longitude for a location.
    """
    geolocator = Nominatim(user_agent="weather_bot")
    try:
        location_data = geolocator.geocode(location_name)
        if location_data:
            latitude = round(location_data.latitude, 2)
            longitude = round(location_data.longitude, 2)
            return latitude, longitude
    except Exception as e:
        print(f"Error in geocoding: {e}")
    return None, None

def get_weather_forecast(latitude, longitude):
    """
    Fetches a 5-day weather forecast from OpenWeatherMap API using latitude and longitude.
    """
    try:
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={WEATHER_TOKEN}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch forecast. Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error in fetching forecast: {e}")
    return None

def fetch_weather(message):
    """
    Handles weather fetching after the user provides a location.
    Adds inline buttons for weather map and air quality options.
    """
    latitude, longitude = location_handler(message.text)
    if latitude is None or longitude is None:
        bot.send_message(message.chat.id, "Location not found. Please try again.")
        return

    forecast = get_weather_forecast(latitude, longitude)
    if forecast:
        forecast_message = "Here is the 5-day forecast for your location:\n\n"
        for day in forecast['list'][::8]:  # Every 8th item represents a new day in the forecast
            day_time = day['dt_txt']
            day_temp = day['main']['temp']
            day_description = day['weather'][0]['description']
            forecast_message += f"Date: {day_time}\nTemperature: {day_temp}°C\nWeather: {day_description.capitalize()}\n\n"

        # Add inline buttons for Weather Map and Air Quality
        markup = types.InlineKeyboardMarkup()

        # Encode latitude and longitude in a safer format (replace . with ,)
        weather_map_button = types.InlineKeyboardButton(
            "Weather Map", callback_data=f"weather_map_{latitude},{longitude}"
        )
        air_quality_button = types.InlineKeyboardButton(
            "Air Quality", callback_data=f"air_quality_{latitude},{longitude}"
        )
        markup.add(weather_map_button, air_quality_button)

        bot.send_message(message.chat.id, forecast_message, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Could not fetch weather data. Please try again.")

def handle_weather_map(call):
    """
    Sends the weather map when the 'Weather Map' button is clicked.
    """
    # Decode latitude and longitude (replace , with .)
    _, latitude, longitude = call.data.split("_")
    latitude = latitude.replace(",", ".")
    longitude = longitude.replace(",", ".")
    map_url = get_weather_map(latitude, longitude)
    bot.send_photo(call.message.chat.id, map_url)

def handle_air_quality(call):
    """
    Sends the air quality index when the 'Air Quality' button is clicked.
    """
    # Decode latitude and longitude (replace , with .)
    _, latitude, longitude = call.data.split("_")
    latitude = float(latitude.replace(",", "."))
    longitude = float(longitude.replace(",", "."))
    air_quality = get_air_quality(latitude, longitude)
    if air_quality:
        aqi = air_quality['list'][0]['main']['aqi']
        air_quality_message = f"The Air Quality Index (AQI) for your location is: {aqi}\n"
        if aqi == 1:
            air_quality_message += "Air Quality: Good"
        elif aqi == 2:
            air_quality_message += "Air Quality: Fair"
        elif aqi == 3:
            air_quality_message += "Air Quality: Moderate"
        elif aqi == 4:
            air_quality_message += "Air Quality: Poor"
        elif aqi == 5:
            air_quality_message += "Air Quality: Very Poor"
        bot.send_message(call.message.chat.id, air_quality_message)
    else:
        bot.send_message(call.message.chat.id, "Could not fetch air quality data. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("weather_map_"))
def weather_map_callback(call):
    """
    Callback handler for the 'Weather Map' button.
    """
    handle_weather_map(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("air_quality_"))
def air_quality_callback(call):
    """
    Callback handler for the 'Air Quality' button.
    """
    handle_air_quality(call)

def get_weather_map(latitude, longitude):
    """
    Fetches the weather map image URL from OpenWeatherMap API for a specific location.
    """
    map_url = f"http://tile.openweathermap.org/map/clouds_new/10/512/341.png?appid={WEATHER_TOKEN}"
    return map_url

def get_air_quality(latitude, longitude):
    """
    Fetches the air quality index from OpenWeatherMap API using latitude and longitude.
    """
    try:
        url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={WEATHER_TOKEN}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        print(f"Error fetching air quality data: {e}")
    return None

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    """
    Echoes back any other message sent by the user.
    """
    bot.reply_to(message, message.text)

# Start the bot
print("Bot is running...")
bot.infinity_polling()


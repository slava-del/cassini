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
    raise ValueError("BOT_TOKEN or WEATHER_TOKEN is missing in environment variables.")

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
        "/weather - Get weather information\n"
        "/air_quality - Get air quality index\n"
        "/weather_map - Get weather maps\n"
        "Simply type a location after choosing an option.\n"
        "Enjoy using the bot!"
    )
    bot.send_message(message.chat.id, help_message)

def location_handler(location_name, user_id):
    """
    Uses the Nominatim geocoder to get latitude and longitude for a location
    and stores it in the user_data dictionary.
    """
    geolocator = Nominatim(user_agent="weather_bot")
    location_data = geolocator.geocode(location_name)
    if location_data:
        latitude = round(location_data.latitude, 2)
        longitude = round(location_data.longitude, 2)
        
        # Store location data for the user
        user_data[user_id] = {'latitude': latitude, 'longitude': longitude}
        return latitude, longitude
    else:
        return None, None

def get_weather_forecast(latitude, longitude):
    """
    Fetches a 5-day weather forecast from OpenWeatherMap API using latitude and longitude.
    """
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={WEATHER_TOKEN}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_air_quality(latitude, longitude):
    """
    Fetches the air quality index from OpenWeatherMap API using latitude and longitude.
    """
    url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={WEATHER_TOKEN}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_map(latitude, longitude):
    """
    Fetches the weather map image URL from OpenWeatherMap API for a specific location.
    """
    # For this example, we'll use a static cloud map layer (clouds view)
    # You can change the map layer type, like temperature or precipitation if needed.
    zoom = 10  # Adjust zoom level if necessary
    x_tile = 512  # Tile coordinates (static)
    y_tile = 341  # Tile coordinates (static)
    map_url = f"http://tile.openweathermap.org/map/clouds_new/{zoom}/{x_tile}/{y_tile}.png?appid={WEATHER_TOKEN}"
    return map_url

def fetch_weather(message):
    """
    Handles weather fetching after the user provides a location.
    """
    latitude, longitude = location_handler(message.text, message.chat.id)
    if latitude is None or longitude is None:
        bot.send_message(message.chat.id, "Location not found. Please try again.")
        return

    forecast = get_weather_forecast(latitude, longitude)
    if forecast:
        forecast_message = "Here is the 5-day forecast for your location:\n\n"
        for day in forecast['list'][::8]:  # Every 8th item represents a new day in the forecast (every 3 hours)
            day_time = day['dt_txt']
            day_temp = day['main']['temp']
            day_description = day['weather'][0]['description']
            
            # Weather map button
            weather_map_button = types.InlineKeyboardButton("Weather Map", callback_data=f"weather_map_{latitude}_{longitude}")
            air_quality_button = types.InlineKeyboardButton("Air Quality", callback_data=f"air_quality_{latitude}_{longitude}")
            
            # Build inline keyboard with weather map and air quality options
            markup = types.InlineKeyboardMarkup()
            markup.add(weather_map_button, air_quality_button)

            # Send the forecast with the buttons
            forecast_message += f"Date: {day_time}\nTemperature: {day_temp}°C\nWeather: {day_description.capitalize()}\n\n"
        
        bot.send_message(message.chat.id, forecast_message, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Could not fetch weather data. Please try again.")

def fetch_air_quality(message):
    """
    Handles air quality fetching after the user provides a location.
    """
    # Retrieve latitude and longitude from user data
    latitude = user_data[message.chat.id].get('latitude')
    longitude = user_data[message.chat.id].get('longitude')

    if latitude is None or longitude is None:
        bot.send_message(message.chat.id, "Location not found. Please try again.")
        return

    air_quality = get_air_quality(latitude, longitude)
    if air_quality:
        # Extract the AQI level and make the message more descriptive
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
        bot.send_message(message.chat.id, air_quality_message)
    else:
        bot.send_message(message.chat.id, "Could not fetch air quality data. Please try again.")

def fetch_weather_map(message):
    """
    Sends the weather map image when a location is provided.
    """
    # Retrieve latitude and longitude from user data
    latitude = user_data[message.chat.id].get('latitude')
    longitude = user_data[message.chat.id].get('longitude')

    if latitude is None or longitude is None:
        bot.send_message(message.chat.id, "Location not found. Please try again.")
        return

    weather_map_url = get_weather_map(latitude, longitude)
    
    # Send the map as an image
    bot.send_photo(message.chat.id, weather_map_url)

@bot.callback_query_handler(func=lambda call: call.data.startswith("weather_map_"))
def handle_weather_map_button(call):
    """
    Handle the button click for 'Weather Map'.
    """
    data = call.data.split("_")
    latitude = data[1]
    longitude = data[2]
    fetch_weather_map(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("air_quality_"))
def handle_air_quality_button(call):
    """
    Handle the button click for 'Air Quality'.
    """
    data = call.data.split("_")
    latitude = data[1]
    longitude = data[2]
    fetch_air_quality(call.message)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    """
    Echoes back any other message sent by the user.
    """
    bot.reply_to(message, message.text)

# Start the bot
print("Bot is running...")
bot.infinity_polling()

from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = 'https://api.openweathermap.org/data/2.5'


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def get_weather():
    """Fetch weather data for a given city (used by the search box via JS)."""
    try:
        if not API_KEY:
            return jsonify({'error': 'Server is missing WEATHER_API_KEY. Check your .env file.'}), 500

        city = request.json.get('city') if request.is_json else None

        if not city:
            return jsonify({'error': 'City name is required'}), 400

        # Current weather
        current_url = f'{BASE_URL}/weather'
        current_response = requests.get(current_url, params={
            'q': city, 'appid': API_KEY, 'units': 'metric'
        })
        current_response.raise_for_status()
        current_data = current_response.json()

        # Forecast (5 days)
        forecast_url = f'{BASE_URL}/forecast'
        forecast_response = requests.get(forecast_url, params={
            'q': city, 'appid': API_KEY, 'units': 'metric'
        })
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Process current weather
        weather_info = {
            'city': current_data['name'],
            'country': current_data['sys']['country'],
            'temperature': round(current_data['main']['temp']),
            'feels_like': round(current_data['main']['feels_like']),
            'humidity': current_data['main']['humidity'],
            'pressure': current_data['main']['pressure'],
            'description': current_data['weather'][0]['description'].title(),
            'icon': current_data['weather'][0]['icon'],
            'wind_speed': round(current_data['wind']['speed'], 1),
            'visibility': round(current_data.get('visibility', 0) / 1000, 1),
            'sunrise': datetime.fromtimestamp(current_data['sys']['sunrise']).strftime('%H:%M:%S'),
            'sunset': datetime.fromtimestamp(current_data['sys']['sunset']).strftime('%H:%M:%S'),
        }

        # Process forecast - one entry roughly every 24 hours
        forecast_list = []
        for item in forecast_data['list'][::8]:
            forecast_list.append({
                'date': datetime.fromtimestamp(item['dt']).strftime('%a, %d %b'),
                'temp_max': round(item['main']['temp_max']),
                'temp_min': round(item['main']['temp_min']),
                'description': item['weather'][0]['description'].title(),
                'icon': item['weather'][0]['icon'],
            })

        weather_info['forecast'] = forecast_list

        return jsonify(weather_info)

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return jsonify({'error': 'City not found'}), 404
        return jsonify({'error': 'Failed to fetch weather data'}), 500
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Could not reach the weather service. Check your connection.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/about')
def about():
    """Render the About page."""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Render the Contact page."""
    return render_template('contact.html')


@app.route('/weather/<city>')
def get_weather_page(city):
    """Render a standalone weather page for a specific city (server-rendered)."""
    try:
        if not API_KEY:
            return render_template('index.html', error='Server is missing WEATHER_API_KEY.'), 500

        current_url = f'{BASE_URL}/weather'
        current_response = requests.get(current_url, params={
            'q': city, 'appid': API_KEY, 'units': 'metric'
        })
        current_response.raise_for_status()
        current_data = current_response.json()

        weather_info = {
            'city': current_data['name'],
            'country': current_data['sys']['country'],
            'temperature': round(current_data['main']['temp']),
            'description': current_data['weather'][0]['description'].title(),
            'icon': current_data['weather'][0]['icon'],
        }

        return render_template('whether.html', weather=weather_info)
    except Exception:
        return render_template('index.html', error='City not found'), 404


if __name__ == '__main__':
    app.run(debug=True)

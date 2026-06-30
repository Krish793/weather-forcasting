async function searchWeather() {
    const cityInput = document.getElementById('cityInput');
    const city = cityInput.value.trim();

    const errorMessage = document.getElementById('errorMessage');
    const weatherContainer = document.getElementById('weatherContainer');

    errorMessage.style.display = 'none';
    weatherContainer.style.display = 'none';

    if (!city) {
        showError('Please enter a city name.');
        return;
    }

    try {
        const response = await fetch('/weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city: city })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Something went wrong.');
            return;
        }

        renderWeather(data);
    } catch (err) {
        showError('Could not reach the server. Please try again.');
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function renderWeather(data) {
    document.getElementById('cityName').textContent = `${data.city}, ${data.country}`;
    document.getElementById('weatherIcon').src = `https://openweathermap.org/img/wn/${data.icon}@4x.png`;
    document.getElementById('temperature').textContent = data.temperature;
    document.getElementById('description').textContent = data.description;
    document.getElementById('feelsLike').textContent = `Feels like ${data.feels_like}°C`;
    document.getElementById('humidity').textContent = data.humidity;
    document.getElementById('pressure').textContent = data.pressure;
    document.getElementById('windSpeed').textContent = data.wind_speed;
    document.getElementById('visibility').textContent = data.visibility;
    document.getElementById('sunrise').textContent = data.sunrise;
    document.getElementById('sunset').textContent = data.sunset;

    const forecastContainer = document.getElementById('forecastContainer');
    forecastContainer.innerHTML = '';

    data.forecast.forEach(day => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <p class="forecast-date">${day.date}</p>
            <img src="https://openweathermap.org/img/wn/${day.icon}@2x.png" alt="${day.description}">
            <p class="forecast-desc">${day.description}</p>
            <p class="forecast-temps"><span class="temp-max">${day.temp_max}°</span> / <span class="temp-min">${day.temp_min}°</span></p>
        `;
        forecastContainer.appendChild(card);
    });

    document.getElementById('weatherContainer').style.display = 'block';
}

// Allow pressing Enter in the input box to trigger a search
document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('cityInput');
    if (cityInput) {
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchWeather();
            }
        });
    }
});

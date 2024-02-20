from django.urls import path
from .views import WeatherViewSet

urlpatterns = [
    path("forecasts/", WeatherViewSet.get_forecast, name="forecast"),
    path("tomorrow/", WeatherViewSet.get_tomorrow_forecast, name="tomorrow_forecast"),
]

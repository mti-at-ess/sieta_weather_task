from datetime import datetime, timezone, timedelta

from django.http import JsonResponse
from rest_framework.viewsets import GenericViewSet
import pandas as pd
from sieta_weather_task import settings
from .utils import get_segregated_data, sort_dataframes_by_belief_fetch_last


class WeatherViewSet(GenericViewSet):
    """
    A view set to handle weather forecast requests.
    """

    def get_forecast(request):
        """
        Retrieves weather forecast based on given 'now' and 'then' parameters.
        """
        now = request.GET.get("now")
        then = request.GET.get("then")

        # Check if 'now' and 'then' parameters are provided
        if now is None or then is None:
            return JsonResponse({"error": "Both parameters are required"}, status=400)

        # Read weather dataset
        dataset = pd.read_csv(settings.WEATHER_DATAFILE)

        try:
            # Convert 'now' and 'then' to datetime objects with timezone information
            now = datetime.fromisoformat(now).replace(tzinfo=timezone.utc)
            then = datetime.fromisoformat(then).replace(tzinfo=timezone.utc)
        except ValueError:
            return JsonResponse(
                {
                    "error": "Invalid datetime format. Please provide ISO format datetime string."
                },
                status=400,
            )

        # Filter relevant data based on provided time range
        relevant_data = dataset[
            (pd.to_datetime(dataset["event_start"]) >= now)
            & (pd.to_datetime(dataset["event_start"]) <= then)
        ]

        # Segregate the data of dataframe into separate sources one.
        temperature_df, irradiance_df, wind_speed_df = get_segregated_data(
            relevant_data
        )

        # Sort relevant data by 'belief_horizon_in_sec'
        temperature_forecast = sort_dataframes_by_belief_fetch_last(temperature_df)
        irradiance_forecast = sort_dataframes_by_belief_fetch_last(irradiance_df)
        wind_speed_forecast = sort_dataframes_by_belief_fetch_last(wind_speed_df)

        return JsonResponse(
            {
                "temperature": temperature_forecast[0] if temperature_forecast else None,
                "irradiance": irradiance_forecast[0] if irradiance_forecast else None,
                "wind_speed": wind_speed_forecast[0] if wind_speed_forecast else None,
            }
        )

    def get_tomorrow_forecast(request):
        """
        Retrieves forecast for tomorrow based on the 'now' parameter.
        """
        now = request.GET.get("now")
        if now is None:
            return JsonResponse({"error": "Both parameters are required"}, status=400)

        # Read weather dataset
        dataset = pd.read_csv(settings.WEATHER_DATAFILE)

        try:
            # Convert 'now' to a datetime object
            now = datetime.fromisoformat(now)
        except ValueError:
            return JsonResponse(
                {
                    "error": "Invalid datetime format. Please provide ISO format datetime string."
                },
                status=400,
            )

        # Extract data for tomorrow
        tomorrow_data = dataset[
            (
                pd.to_datetime(dataset["event_start"]).dt.date
                == (now + timedelta(days=1)).date()
            )
        ]

        # Separate data for temperature, irradiance, and wind_speed sensors

        temperature_df, irradiance_df, wind_speed_df = get_segregated_data(
            tomorrow_data
        )

        # Check if it's warm, sunny, and windy based on threshold values
        is_warm = any(
            temperature_df["event_value"].apply(
                lambda x: x >= int(settings.WARM_THRESHOLD)
            )
        )
        is_sunny = any(
            irradiance_df["event_value"].apply(
                lambda x: x >= int(settings.SUNNY_THRESHOLD)
            )
        )
        is_windy = any(
            wind_speed_df["event_value"].apply(
                lambda x: x >= int(settings.WINDY_THRESHOLD)
            )
        )

        return JsonResponse(
            {"is_warm": is_warm, "is_sunny": is_sunny, "is_windy": is_windy}
        )

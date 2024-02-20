from datetime import datetime, timezone, timedelta

from django.http import JsonResponse
from rest_framework.viewsets import GenericViewSet
import pandas as pd
from sieta_weather_task import settings


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
        temperature_df = relevant_data.loc[
            relevant_data["sensor"].str.contains("temperature")
        ]
        irradiance_df = relevant_data.loc[
            relevant_data["sensor"].str.contains("irradiance")
        ]
        wind_speed_df = relevant_data.loc[
            relevant_data["sensor"].str.contains("wind_speed")
        ]

        # Sort relevant data by 'belief_horizon_in_sec'
        sorted_temperature_df = temperature_df.sort_values(
            by="belief_horizon_in_sec", key=pd.to_datetime, ascending=True
        )
        sorted_irradiance_df = irradiance_df.sort_values(
            by="belief_horizon_in_sec", key=pd.to_datetime, ascending=True
        )
        sorted_wind_speed_df = wind_speed_df.sort_values(
            by="belief_horizon_in_sec", key=pd.to_datetime, ascending=True
        )

        # Get the top 3 forecasts
        temperature_forecast = sorted_temperature_df.head(1).to_dict("records")
        irradiance_forecast = sorted_irradiance_df.head(1).to_dict("records")
        wind_speed_forecast = sorted_wind_speed_df.head(1).to_dict("records")

        return JsonResponse(
            {"temperature": temperature_forecast, "irradiance": irradiance_forecast, "wind_speed": wind_speed_forecast})

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
        temperature_df = tomorrow_data.loc[
            tomorrow_data["sensor"].str.contains("temperature")
        ]
        irradiance_df = tomorrow_data.loc[
            tomorrow_data["sensor"].str.contains("irradiance")
        ]
        wind_speed_df = tomorrow_data.loc[
            tomorrow_data["sensor"].str.contains("wind_speed")
        ]

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

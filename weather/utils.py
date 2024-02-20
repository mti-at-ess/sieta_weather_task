import pandas as pd


def get_segregated_data(dataframe):
    """
    Segregates data from the given DataFrame into temperature, irradiance, and wind speed DataFrames.

    Parameters:
        dataframe (pandas.DataFrame): The DataFrame containing weather data.

    Returns:
        tuple: A tuple containing temperature, irradiance, and wind speed DataFrames.
    """
    # Filter data for temperature, irradiance, and wind speed sensors
    temperature_df = dataframe.loc[dataframe["sensor"].str.contains("temperature")]
    irradiance_df = dataframe.loc[dataframe["sensor"].str.contains("irradiance")]
    wind_speed_df = dataframe.loc[dataframe["sensor"].str.contains("wind speed")]

    return temperature_df, irradiance_df, wind_speed_df


def sort_dataframes_by_belief_fetch_last(dataframe):
    """
    Sorts the DataFrame by 'belief_horizon_in_sec' in ascending order and fetches the last record.

    Parameters:
        dataframe (pandas.DataFrame): The DataFrame to be sorted.

    Returns:
        dict: A dictionary representing the last record after sorting.
    """
    # Sort the DataFrame by 'belief_horizon_in_sec' in ascending order and fetch the last record
    return dataframe.sort_values(
        by="belief_horizon_in_sec", key=pd.to_datetime, ascending=True
    ).head(1).to_dict("records")
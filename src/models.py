# src/models.py

import numpy as np
import pandas as pd
from typing import List, Dict
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TrafficData:
    def __init__(self, axle_loads: List[float], traffic_growth_rate: float, analysis_period: int):
        """
        Initialize TrafficData with axle loads, growth rate, and analysis period.

        :param axle_loads: List of axle loads in kN.
        :param traffic_growth_rate: Annual traffic growth rate (decimal, e.g., 0.02 for 2%).
        :param analysis_period: Number of years for analysis.
        """
        self.axle_loads = axle_loads
        self.traffic_growth_rate = traffic_growth_rate
        self.analysis_period = analysis_period

    def get_total_axle_loads(self) -> List[List[float]]:
        """
        Project total axle loads over the analysis period considering growth rate.

        :return: A list of lists, each sublist represents axle loads for a year.
        """
        total_loads = []
        for year in range(self.analysis_period):
            growth_factor = (1 + self.traffic_growth_rate) ** year
            projected_loads = [load * growth_factor for load in self.axle_loads]
            total_loads.append(projected_loads)
            logger.debug(f"Year {year + 1}: {projected_loads}")
        return total_loads

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> 'TrafficData':
        """
        Create TrafficData instance from a pandas DataFrame.

        :param df: DataFrame with columns 'Axle_Loads', 'Traffic_Growth_Rate', 'Analysis_Period'.
        :return: TrafficData instance.
        """
        try:
            axle_loads = df['Axle_Loads'].dropna().tolist()
            traffic_growth_rate = float(df['Traffic_Growth_Rate'].iloc[0])
            analysis_period = int(df['Analysis_Period'].iloc[0])
            logger.info("TrafficData loaded successfully from DataFrame.")
            return TrafficData(axle_loads, traffic_growth_rate, analysis_period)
        except Exception as e:
            logger.error(f"Error creating TrafficData from DataFrame: {e}")
            raise ValueError(f"Invalid Traffic Data: {e}")


class ClimateData:
    def __init__(self, average_temperature: float, temperature_variation: float, rainfall: float):
        """
        Initialize ClimateData with average temperature, temperature variation, and rainfall.

        :param average_temperature: Average temperature in °C.
        :param temperature_variation: Temperature variation in °C.
        :param rainfall: Annual rainfall in mm.
        """
        self.average_temperature = average_temperature
        self.temperature_variation = temperature_variation
        self.rainfall = rainfall

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> 'ClimateData':
        """
        Create ClimateData instance from a pandas DataFrame.

        :param df: DataFrame with columns 'Average_Temperature', 'Temperature_Variation', 'Rainfall'.
        :return: ClimateData instance.
        """
        try:
            average_temperature = float(df['Average_Temperature'].iloc[0])
            temperature_variation = float(df['Temperature_Variation'].iloc[0])
            rainfall = float(df['Rainfall'].iloc[0])
            logger.info("ClimateData loaded successfully from DataFrame.")
            return ClimateData(average_temperature, temperature_variation, rainfall)
        except Exception as e:
            logger.error(f"Error creating ClimateData from DataFrame: {e}")
            raise ValueError(f"Invalid Climate Data: {e}")


class SubgradeProperties:
    def __init__(self, modulus: float, CBR: float):
        """
        Initialize SubgradeProperties with modulus and California Bearing Ratio (CBR).

        :param modulus: Modulus of subgrade reaction in kPa/m.
        :param CBR: California Bearing Ratio in %.
        """
        self.modulus = modulus
        self.CBR = CBR

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> 'SubgradeProperties':
        """
        Create SubgradeProperties instance from a pandas DataFrame.

        :param df: DataFrame with columns 'Modulus', 'CBR'.
        :return: SubgradeProperties instance.
        """
        try:
            modulus = float(df['Modulus'].iloc[0])
            CBR = float(df['CBR'].iloc[0])
            logger.info("SubgradeProperties loaded successfully from DataFrame.")
            return SubgradeProperties(modulus, CBR)
        except Exception as e:
            logger.error(f"Error creating SubgradeProperties from DataFrame: {e}")
            raise ValueError(f"Invalid Subgrade Properties Data: {e}")


class MaterialProperties:
    def __init__(self, asphalt_modulus: float, concrete_strength: float, thermal_coeff: float):
        """
        Initialize MaterialProperties with asphalt modulus, concrete strength, and thermal coefficient.

        :param asphalt_modulus: Asphalt modulus in MPa.
        :param concrete_strength: Concrete strength in MPa.
        :param thermal_coeff: Thermal coefficient (°C^-1).
        """
        self.asphalt_modulus = asphalt_modulus
        self.concrete_strength = concrete_strength
        self.thermal_coeff = thermal_coeff

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> 'MaterialProperties':
        """
        Create MaterialProperties instance from a pandas DataFrame.

        :param df: DataFrame with columns 'Asphalt_Modulus', 'Concrete_Strength', 'Thermal_Coeff'.
        :return: MaterialProperties instance.
        """
        try:
            asphalt_modulus = float(df['Asphalt_Modulus'].iloc[0])
            concrete_strength = float(df['Concrete_Strength'].iloc[0])
            thermal_coeff = float(df['Thermal_Coeff'].iloc[0])
            logger.info("MaterialProperties loaded successfully from DataFrame.")
            return MaterialProperties(asphalt_modulus, concrete_strength, thermal_coeff)
        except Exception as e:
            logger.error(f"Error creating MaterialProperties from DataFrame: {e}")
            raise ValueError(f"Invalid Material Properties Data: {e}")


class Pavement:
    def __init__(self, layers: List[float], pavement_type: str = 'Flexible'):
        """
        Initialize Pavement structure.

        :param layers: List of layer thicknesses in mm.
        :param pavement_type: Type of pavement ('Flexible', 'Rigid', 'Composite').
        """
        self.layers = layers
        self.pavement_type = pavement_type

    def add_layer(self, thickness: float):
        """
        Add a new layer to the pavement structure.

        :param thickness: Thickness of the new layer in mm.
        """
        self.layers.append(thickness)
        logger.debug(f"Added layer: {thickness} mm. Total layers: {self.layers}")

    def remove_layer(self, index: int):
        """
        Remove a layer from the pavement structure by index.

        :param index: Index of the layer to remove.
        """
        if 0 <= index < len(self.layers):
            removed = self.layers.pop(index)
            logger.debug(f"Removed layer at index {index}: {removed} mm. Remaining layers: {self.layers}")
        else:
            logger.warning(f"Attempted to remove non-existent layer at index {index}.")

    def set_pavement_type(self, pavement_type: str):
        """
        Set the type of pavement.

        :param pavement_type: Type of pavement ('Flexible', 'Rigid', 'Composite').
        """
        if pavement_type in ['Flexible', 'Rigid', 'Composite']:
            self.pavement_type = pavement_type
            logger.debug(f"Pavement type set to {pavement_type}.")
        else:
            logger.error(f"Invalid pavement type: {pavement_type}. Must be 'Flexible', 'Rigid', or 'Composite'.")
            raise ValueError("Invalid pavement type. Choose from 'Flexible', 'Rigid', or 'Composite'.")

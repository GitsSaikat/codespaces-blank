# src/performance.py

import logging
from typing import Dict

from src.models import Pavement, TrafficData, ClimateData, SubgradeProperties, MaterialProperties
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def predict_fatigue_cracking(pavement: Pavement, traffic_data: TrafficData, material_props: MaterialProperties) -> float:
    """
    Predict fatigue cracking based on axle loads and material properties.

    :param pavement: Pavement structure.
    :param traffic_data: Traffic data.
    :param material_props: Material properties.
    :return: Total fatigue damage.
    """
    total_damage = 0
    axle_loads = traffic_data.get_total_axle_loads()
    for year, loads in enumerate(axle_loads):
        for load in loads:
            damage = (load / material_props.asphalt_modulus) ** 3  # Simplified relationship
            total_damage += damage
            logger.debug(f"Year {year + 1}, Load {load} kN: Damage {damage}")
    logger.info(f"Total Fatigue Damage: {total_damage}")
    return total_damage


def predict_rutting(pavement: Pavement, traffic_data: TrafficData, climate_data: ClimateData, subgrade_props: SubgradeProperties) -> float:
    """
    Predict rutting based on axle loads, climate data, and subgrade properties.

    :param pavement: Pavement structure.
    :param traffic_data: Traffic data.
    :param climate_data: Climate data.
    :param subgrade_props: Subgrade properties.
    :return: Total rutting depth.
    """
    total_rut = 0
    axle_loads = traffic_data.get_total_axle_loads()
    for year, loads in enumerate(axle_loads):
        for load in loads:
            rut = (load / subgrade_props.modulus) * (climate_data.rainfall / 1000)  # Simplified relationship
            total_rut += rut
            logger.debug(f"Year {year + 1}, Load {load} kN: Rut {rut} mm")
    logger.info(f"Total Rutting: {total_rut} mm")
    return total_rut


def predict_thermal_cracking(pavement: Pavement, climate_data: ClimateData, material_props: MaterialProperties) -> float:
    """
    Predict thermal cracking based on temperature variation and material properties.

    :param pavement: Pavement structure.
    :param climate_data: Climate data.
    :param material_props: Material properties.
    :return: Thermal cracking index.
    """
    thermal_crack = material_props.thermal_coeff * climate_data.temperature_variation
    logger.info(f"Thermal Cracking Index: {thermal_crack}")
    return thermal_crack


def design_new_pavement(pavement: Pavement, traffic_data: TrafficData, climate_data: ClimateData,
                       subgrade_props: SubgradeProperties, material_props: MaterialProperties) -> Dict[str, float]:
    """
    Design a new pavement by predicting various distresses.

    :param pavement: Pavement structure.
    :param traffic_data: Traffic data.
    :param climate_data: Climate data.
    :param subgrade_props: Subgrade properties.
    :param material_props: Material properties.
    :return: Dictionary with predicted distresses.
    """
    fatigue = predict_fatigue_cracking(pavement, traffic_data, material_props)
    rutting = predict_rutting(pavement, traffic_data, climate_data, subgrade_props)
    thermal = predict_thermal_cracking(pavement, climate_data, material_props)
    logger.info("Pavement design simulation completed.")
    return {
        'Fatigue Cracking': fatigue,
        'Rutting': rutting,
        'Thermal Cracking': thermal
    }


def evaluate_performance(pavement: Pavement, traffic_data: TrafficData, climate_data: ClimateData,
                        subgrade_props: SubgradeProperties, material_props: MaterialProperties) -> Dict[str, float]:
    """
    Evaluate pavement performance, currently mirrors design_new_pavement.

    :param pavement: Pavement structure.
    :param traffic_data: Traffic data.
    :param climate_data: Climate data.
    :param subgrade_props: Subgrade properties.
    :param material_props: Material properties.
    :return: Dictionary with predicted distresses.
    """
    logger.info("Evaluating pavement performance.")
    return design_new_pavement(pavement, traffic_data, climate_data, subgrade_props, material_props)

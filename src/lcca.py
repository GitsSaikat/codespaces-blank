# src/lcca.py

import logging
from typing import Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def calculate_LCCA(initial_cost: float, maintenance_costs: Dict[int, float], discount_rate: float, analysis_period: int) -> float:
    """
    Calculate the Life-Cycle Cost Analysis (LCCA) for the pavement.

    :param initial_cost: Initial construction cost.
    :param maintenance_costs: Maintenance costs with year as key.
    :param discount_rate: Annual discount rate (decimal, e.g., 0.03 for 3%).
    :param analysis_period: Number of years to analyze.
    :return: Present value of total lifecycle costs.
    """
    lcc = initial_cost
    logger.info(f"Initial Cost: ${initial_cost:,.2f}")
    for year in range(1, analysis_period + 1):
        maintenance_cost = maintenance_costs.get(year, 0)
        discounted_cost = maintenance_cost / ((1 + discount_rate) ** year)
        lcc += discounted_cost
        if maintenance_cost > 0:
            logger.debug(f"Year {year}: Maintenance Cost ${maintenance_cost:,.2f}, Discounted Cost ${discounted_cost:,.2f}")
    logger.info(f"Total Lifecycle Cost (LCCA): ${lcc:,.2f}")
    return lcc


def perform_LCCA(initial_cost: float, maintenance_costs: Dict[int, float], discount_rate: float, analysis_period: int) -> float:
    """
    Wrapper function to perform LCCA.

    :param initial_cost: Initial construction cost.
    :param maintenance_costs: Maintenance costs with year as key.
    :param discount_rate: Annual discount rate.
    :param analysis_period: Number of years to analyze.
    :return: Present value of total lifecycle costs.
    """
    logger.info("Starting Life-Cycle Cost Analysis (LCCA).")
    return calculate_LCCA(initial_cost, maintenance_costs, discount_rate, analysis_period)

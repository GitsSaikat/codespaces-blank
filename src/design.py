# src/design.py

from typing import List, Tuple

def design_pavement_structure(layers: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """
    Process the defined pavement layers and structure.

    :param layers: List of tuples containing layer type and thickness.
    :return: List of tuples representing the pavement design.
    """
    try:
        pavement_design = layers  # In this simple case, just return the layers as is
        return pavement_design
    except Exception as e:
        raise ValueError(f"Error in pavement structure design: {e}")

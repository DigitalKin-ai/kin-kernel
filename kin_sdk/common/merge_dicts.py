"""
This module provides a function to merge two dictionaries recursively.
"""

from typing import Dict, Any


def merge_dicts_old(accumulated_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> None:
    """Recursively merge new_dict into accumulated_dict."""
    for key, value in new_dict.items():
        if key in accumulated_dict:
            if isinstance(value, dict) and isinstance(accumulated_dict[key], dict):
                merge_dicts_old(accumulated_dict[key], value)
            elif isinstance(value, list) and isinstance(accumulated_dict[key], list):
                # Merge lists without duplicating elements
                for item in value:
                    if item not in accumulated_dict[key]:
                        accumulated_dict[key].append(item)
            else:
                accumulated_dict[key] = value
        else:
            accumulated_dict[key] = value


def merge_dicts(
    accumulated_dict: Dict[str, Any], new_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fusionne récursivement new_dict dans accumulated_dict et retourne le dictionnaire fusionné.

    :param accumulated_dict: Le dictionnaire accumulé dans lequel fusionner new_dict.
    :type accumulated_dict: Dict[str, Any]
    :param new_dict: Le nouveau dictionnaire à fusionner dans accumulated_dict.
    :type new_dict: Dict[str, Any]
    :return: Le dictionnaire fusionné.
    :rtype: Dict[str, Any]
    """
    merged_dict = accumulated_dict.copy()
    for key, value in new_dict.items():
        if key in merged_dict:
            if isinstance(value, dict) and isinstance(merged_dict[key], dict):
                merged_dict[key] = merge_dicts(merged_dict[key], value)
            elif isinstance(value, list) and isinstance(merged_dict[key], list):
                # Fusionne les listes sans dupliquer les éléments
                merged_dict[key] = merged_dict[key] + [
                    item for item in value if item not in merged_dict[key]
                ]
            else:
                merged_dict[key] = value
        else:
            merged_dict[key] = value
    return merged_dict

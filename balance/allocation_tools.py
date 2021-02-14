from typing import Dict

from data_types import Security


Allocations = Dict[Security, float]


def _normalize_percentages_to_value(allocations: Allocations, value: float) -> Allocations:
    sum_of_percentages = sum(allocations.values())
    return {sec: percent * value / sum_of_percentages for sec, percent in allocations}


def normalize_percentages(allocations: Allocations) -> Allocations:
    return _normalize_percentages_to_value(allocations, 1.0)


def set_single_allocation(allocations: Allocations, security: Security, percentage_to_set: float) -> Allocations:
    if percentage_to_set < 0.0 or percentage_to_set > 1.0:
        raise ValueError('Cannot set a percentage out of bounds')

    remaining_total_allocation = 1.0 - percentage_to_set
    other_allocations = {sec: value for sec, value in allocations if sec != security}

    result_allocations = _normalize_percentages_to_value(other_allocations, remaining_total_allocation)
    result_allocations[security] = percentage_to_set
    return result_allocations

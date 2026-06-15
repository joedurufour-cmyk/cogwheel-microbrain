from copy import deepcopy


EMPTY_VALUES = {None, "", "none", "None", "NONE"}


def keep_if_empty(old_value, new_value):
    if new_value in EMPTY_VALUES:
        return old_value
    return new_value


def merge_dicts(old_value: dict | None, new_value: dict | None) -> dict:
    merged = deepcopy(old_value or {})
    for key, value in (new_value or {}).items():
        if value not in EMPTY_VALUES:
            merged[key] = value
    return merged


def append_unique(old_value: list | None, new_value: list | None) -> list:
    merged = list(old_value or [])
    for item in new_value or []:
        if item not in EMPTY_VALUES and item not in merged:
            merged.append(item)
    return merged


def reduce_universal_state(previous: dict, update: dict) -> dict:
    return {
        **previous,
        "objective": keep_if_empty(previous.get("objective"), update.get("objective")),
        "central_object": keep_if_empty(previous.get("central_object"), update.get("central_object")),
        "active_domain": keep_if_empty(previous.get("active_domain"), update.get("active_domain")),
        "io_contract": merge_dicts(previous.get("io_contract"), update.get("io_contract")),
        "domain_parameters": merge_dicts(previous.get("domain_parameters"), update.get("domain_parameters")),
        "blocking_gap": update.get("blocking_gap", previous.get("blocking_gap")),
        "next_move": keep_if_empty(previous.get("next_move"), update.get("next_move")),
    }


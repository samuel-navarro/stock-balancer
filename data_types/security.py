from dataclasses import dataclass


@dataclass(frozen=True)
class Security:
    identifier: str

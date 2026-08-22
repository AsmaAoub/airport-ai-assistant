from dataclasses import dataclass, field


@dataclass
class AirportEntities:
    """
    Information extracted from the user's request.
    """

    flight_number: str | None = None

    gate: str | None = None

    terminal: str | None = None

    destination: str | None = None

    airport_service: str | None = None

    baggage_reference: str | None = None

    raw: dict = field(default_factory=dict)
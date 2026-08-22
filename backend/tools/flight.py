class FlightTool:
    """
    Tool responsible for retrieving flight information.

    For now, this is a mock implementation.
    Later, it will be connected to a real airport API.
    """

    def __init__(self):
        self.flights = {
            "AT123": {
                "flight_number": "AT123",
                "status": "on_time",
                "gate": "B42",
                "terminal": "1",
            },
            "AF456": {
                "flight_number": "AF456",
                "status": "delayed",
                "gate": "A12",
                "terminal": "2",
            },
        }

    async def get_flight(
        self,
        flight_number: str,
    ) -> dict:

        flight_number = flight_number.upper()

        flight = self.flights.get(flight_number)

        if flight is None:
            return {
                "found": False,
                "flight_number": flight_number,
                "message": "Flight not found.",
            }

        return {
            "found": True,
            "flight": flight,
        }
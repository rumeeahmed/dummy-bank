from pydantic import BaseModel


class Coordinates(BaseModel):
    longitude: str
    latitude: str

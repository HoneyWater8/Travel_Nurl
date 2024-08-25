from pydantic import BaseModel


class PlaceBase(BaseModel):
    name: str
    description: str = None  # type: ignore


class PlaceCreate(PlaceBase):
    pass


class Place(PlaceBase):
    id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field, ConfigDict
from enums.locations import Locations

class Movies(BaseModel):
    id: int
    name: str
    price: int
    description: str
    imageUrl: str
    location: Locations = Field(..., description="Возможные локации при запросе")
    published: bool
    genreId: int
    createdAt: str
    rating: int

    model_config = ConfigDict(use_enum_values=True)

class GettingMovies(BaseModel):
    movies: list[Movies] = Field(..., description="Лист с доп. параметрами")
    count: int
    page: int
    page_size: int = Field(alias="pageSize")
    page_count: int = Field(alias="pageCount")



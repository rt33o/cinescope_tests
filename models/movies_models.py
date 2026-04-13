from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from enums.locations import Locations
from typing import List, Optional

# =================================Получение афиш фильмов=================================
class Movies(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: int = Field(gt=0)
    description: str
    imageUrl: HttpUrl
    location: Locations = Field(..., description="Возможные локации при запросе")
    published: bool
    genreId: int
    createdAt: str
    rating: int

    model_config = ConfigDict(use_enum_values=True)

class GettingMovies(BaseModel):
    movies: list[Movies] = Field(..., description="Лист с доп. параметрами")
    count: int = Field(gt=0)
    page: int = Field(gt=0)
    page_size: int = Field(alias="pageSize")
    page_count: int = Field(alias="pageCount")

# =================================Создание афиш фильмов=================================
class CreateMovie(BaseModel):
    name: str
    image_URL: HttpUrl = Field(alias='imageUrl')
    price: int = Field(gt=0)
    description: str
    location: Locations
    published: bool
    genreId: int

# =================================Получение фильма по ID=================================
class Genre(BaseModel):
    name: str

class User(BaseModel):
    fullName: str

class Review(BaseModel):
    userId: str
    rating: int
    text: str
    createdAt: datetime
    user: User

class GettingMovieById(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: int = Field(gt=0)
    description: str
    imageUrl: HttpUrl  # Валидирует строку как правильный URL
    location: Locations
    published: bool
    genreId: int
    genre: Genre
    createdAt: datetime
    rating: int
    reviews: List[Review]

# =================================Удаление фильма=================================
class DeleteMovie(BaseModel):
    id: int = Field(gt=0)
    name: str
    price: int = Field(gt=0)
    description: str
    imageUrl: HttpUrl
    location: Locations
    published: bool
    genreId: int
    genre: Genre
    createdAt: datetime
    rating: int

class UpdateMovie(BaseModel):
    name: str
    description: str
    price: int = Field(gt=0)
    location: Locations
    imageUrl: HttpUrl
    published: bool
    genreId: int
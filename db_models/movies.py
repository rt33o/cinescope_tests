from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float
from sqlalchemy.orm import declarative_base
from typing import Dict, Any

Base = declarative_base()

class MovieDBModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)  # serial4 -> Integer
    name = Column(String)                   # text -> String
    price = Column(Integer)                 # int4 -> Integer
    description = Column(String)            # text -> String
    image_url = Column(String)              # text -> String
    location = Column(String)               # custom Location enum -> String
    published = Column(Boolean)             # bool -> Boolean
    rating = Column(Float)                  # float8 -> Float
    genre_id = Column(Integer)              # int4 -> Integer
    created_at = Column(DateTime)           # timestamp(3) -> DateTime

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование модели в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<Movie(id={self.id}, name='{self.name}')>"
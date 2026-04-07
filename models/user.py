# from pydantic import BaseModel, Field, EmailStr
# from typing import List
# from enum import Enum
#
# class RegistrationUserModel(BaseModel):
#     email: EmailStr
#     full_name: str = Field(..., alias="fullName")
#     password: str
#     password_repeat: str = Field(..., alias="passwordRepeat")
#     roles: List[str]
#
#     class Config:
#         populate_by_name = True
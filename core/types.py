import strawberry
import strawberry_django
from strawberry import auto
from typing import Optional,Any

from . import models


    
@strawberry_django.type(models.Tag)
class Tag:
    id:auto
    name:auto
    fruit:list['Fruit']
    created_at:auto
    updated_at:auto
    
@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color: 'Color'
    tags:list[Tag]
    nb_tags:int
    created_at:auto
    updated_at:auto

@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: list[Fruit]
    created_at:auto
    updated_at:auto


@strawberry.type
class Message:
    success: bool
    message: str


@strawberry_django.type(models.Tag)
class Filter:
    id:auto
    fruit:'Fruit'
    tag:'Tag'
    created_at:auto
    updated_at:auto
    
@strawberry.type
class AuthPayload:
    token: str
    username: str
    
@strawberry.type
class UserType:
    id: strawberry.ID
    username: str
    email: str | None = None
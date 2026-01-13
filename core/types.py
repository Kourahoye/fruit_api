import datetime
import strawberry
import strawberry_django
from strawberry import auto
from typing import Optional,Any
from . import models
from strawberry.file_uploads import Upload

    
@strawberry_django.type(models.Tag)
class Tag:
    id:auto
    name:auto
    fruit: Optional[list['Fruit']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    
@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color: 'Color'
    tags:list[Tag]
    nbTags:Optional[int]
    created_at:auto
    updated_at:auto
    description:Optional[str]=None
    image : auto
    #image_url: auto   # ← lecture

    # @strawberry.field
    # def image_url(self) -> Optional[str]:
    #     return self.image.url if self.image else None
    
    @strawberry.field
    def nbTags(self) -> int:
        return self.tags.count()

@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    hexCode:Optional[str]=None
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
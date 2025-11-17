import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension
from . import models
from core import models
from django.db.models import Count
from .types import Color, Fruit,Message, Tag,Filter,AuthPayload, UserType
import jwt
import datetime
from django.contrib.auth import authenticate
from strawberry.types import Info
from django.conf import settings
from django.contrib.auth.models import User
from gqlauth.user.queries import UserQueries
from gqlauth.core.middlewares import JwtSchema

@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field()
    colors: list[Color] = strawberry_django.field()
    tags:   list[Tag]=strawberry_django.field()
    get_color:list[Color]
    get_fruit_by_tag:list[Tag]
    get_fruit_by_multiple_tag:list[Fruit]
    
    
    @strawberry.field
    def me(self, info: Info) -> UserType | None:
        user = info.context.request.user
        if user and user.is_authenticated:
            return user
        return None
    
    @strawberry.field
    def get_color(self, name: str):
        color = models.Color.objects.filter(name=name)
        return color
    
    @strawberry.field
    def get_fruit_by_tag(self, name: str):
        tag = models.Tag.objects.filter(name=name)
        return tag
    
    @strawberry.field
    def get_fruit_by_multiple_tag(self,incl:list[str]=[],excl:list[str]=[]) -> Fruit:
        if len(incl) == 1:
            incl_id = models.Tag.objects.filter(name=incl[0])
        else:
            incl_id = models.Tag.objects.filter(name__in=incl)
        
        if len(excl) == 1:
            excl_id = models.Tag.objects.filter(name=excl[0])
        else:
            excl_id = models.Tag.objects.filter(name__in=excl)
            
        fruits = models.Fruit.objects.all().order_by("id").annotate(nb_tags=Count("filter"))
        
        for i in incl_id:
            fruits= fruits.filter(tags=i)

        if excl_id:
            for i in excl_id:
                fruits= fruits.exclude(tags=i)

        return fruits




    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_color(self, name: str) -> Color:
        print(f"Adding {name}")
        color = models.Color.objects.create(name=name)
        return color


    @strawberry.mutation
    def add_fruit(self, name: str, color_id: int) -> Fruit:
        color = models.Color.objects.get(pk=color_id)
        fruit = models.Fruit.objects.create(name=name, color=color)
        return fruit
    
    @strawberry.mutation
    def add_tag(self,name:str) ->Tag:
        tag = models.Tag.objects.create(name=name)
        return tag
    
    @strawberry.mutation
    def add_tag_to_fruit(self,fruit_name:str,tag_name:str) ->Message:
        tag = models.Tag.objects.get(name=tag_name)
        fruit = models.Fruit.objects.get(name=fruit_name)
        try:
            filtre =models.Filter.objects.create(fruit=fruit,tag=tag)
            return Message(success=True,message="Tag ajouter")
        except :
            return Message(success=False,message="Ajout du tag echouer")
        
        
    @strawberry.mutation
    def delete_color(self, id: int) -> Message:
        try:
            color = models.Color.objects.get(pk=id)
            color.delete()
            return Message(success=True,message="Color deleted successfully")
        except models.Color.DoesNotExist:
            return Message(success=False,message="Color not found")

    
    @strawberry.mutation
    def update_color(self, id: int, name: str) -> Message:
        try:
            color = models.Color.objects.get(pk=id)
            color.name = name
            color.save()
            return Message(success=True, message="Color updated successfully")
        except models.Color.DoesNotExist:
            return Message(success=False, message="Color not found")
        
    @strawberry.mutation
    def update_fruit(self, id: int, name: str) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=id)
            fruit.name = name
            fruit.save()
            return Message(success=True, message="Fruit updated successfully")
        except models.Fruit.DoesNotExist:
            return Message(success=False, message="Fruit not found")
        
    @strawberry.mutation
    def remove_tag(self, fruit_id: int, tag_id: int) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=fruit_id)
            tag = models.Tag.objects.get(id=tag_id)
            filtre = models.Filter.objects.get(fruit=fruit,tag=tag)
            filtre.delete()
            return Message(success=True, message="Tag removed successfully")
        except models.Filter.DoesNotExist:
            return Message(success=False, message="Tag not found for this object")
    
    @strawberry.mutation
    def delete_fruit(self, id: int) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=id)
            fruit.delete()
            return Message(success=True,message="Fruit deleted successfully")
        except models.Fruit.DoesNotExist:
            return Message(success=False,message="Fruit not found")
    
    @strawberry.type
    class Mutation:
        @strawberry.mutation
        def login(self, info: Info, username: str, password: str) -> AuthPayload | None:
            user = authenticate(username=username, password=password)
            if not user:
                return None

            payload = {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            }

            token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

            return AuthPayload(token=token, username=user.username)


    
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,  # not required, but highly recommended
    ],
)
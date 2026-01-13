import strawberry
import strawberry_django

from core.permissions import IsAuthenticated
from . import models
from core import models
from django.db.models import Count
from .types import Color, Fruit,Message, Tag, UserType
from django.conf import settings
from django.core.exceptions import ValidationError
from gqlauth.user import arg_mutations as mutations
from gqlauth.user.queries import UserQueries
from gqlauth.core.middlewares import JwtSchema
from gqlauth.user.queries import UserQueries, UserType
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from gqlauth.core.middlewares import JwtSchema
from strawberry.file_uploads import Upload
from typing import Optional
@strawberry.django.type(model=get_user_model())
class MyQueries:
    me: UserType = UserQueries.me
    public: UserType = UserQueries.public_user

@strawberry.type
class Query(UserQueries):
    fruits: list[Fruit] = strawberry_django.field(permission_classes=[IsAuthenticated])
    colors: list[Color] = strawberry_django.field(permission_classes=[IsAuthenticated])
    tags:   list[Tag]=strawberry_django.field(permission_classes=[IsAuthenticated])
    get_color:list[Color]
    get_fruit_by_tag:list[Tag]
    get_fruit_by_multiple_tag:list[Fruit]
    get_fruit:Fruit
    get_fruit_by_name:list[Fruit]
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_color(self, name: str):
        color = models.Color.objects.filter(name=name)
        return color
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_fruit(self, id: int) -> Fruit:
        fruit = models.Fruit.objects.get(pk=id)
        return fruit 
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_fruit_by_name(self, name: str)->list[Fruit]:
        fruit = models.Fruit.objects.filter(name__startswith=name)
        return fruit
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_fruit_by_tag(self, name: str):
        tag = models.Tag.objects.filter(name=name)
        return tag
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_fruit_by_multiple_tag(self,incl:list[str]=[],excl:list[str]=[]) -> Fruit:
        if len(incl) == 1:
            incl_id = models.Tag.objects.filter(name=incl[0])
        else:
            incl_id = models.Tag.objects.filter(name__in=incl)
        
        if len(excl) == 1:
            excl_id = models.Tag.objects.filter(name=excl[0])
        else:
            excl_id = models.Tag.objects.filter(name__in=excl)
            
        fruits = models.Fruit.objects.all().order_by("id")
        
        for i in incl_id:
            fruits= fruits.filter(tags=i)

        if excl_id:
            for i in excl_id:
                fruits= fruits.exclude(tags=i)

        return fruits
    
@strawberry.type
class Mutation:
    register = mutations.Register.field
    verify_account = mutations.VerifyAccount.field
    token_auth = mutations.ObtainJSONWebToken.field
    refresh_token = mutations.RefreshToken.field
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def add_color(self, name: str,hexval:str) -> Color:
        #is valid hexadecimal test
        if not hexval.startswith('#') or len(hexval) != 7 or not all(c in '0123456789ABCDEFabcdef' for c in hexval[1:]):
            raise ValidationError("La valeur hexadecimal est incorrecte")
        color = models.Color.objects.create(name=name, hexCode=hexval)
        return color


    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def add_fruit(
        self,
        name: str,
        color_id: int,
        description: str | None = None,
        image: Optional[Upload] = None,   
    ) -> Fruit:
        
        color = models.Color.objects.get(pk=color_id)

        fruit = models.Fruit.objects.create(
            name=name,
            color=color,
            description=description
        )

        if image:
            fruit.image.save(image.name, image, save=True)

        return fruit
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def add_tag(self,info,name:str) ->Tag:
        print(info)
        tag = models.Tag.objects.create(name=name)
        return Tag(id=tag.id, name=tag.name)
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def add_tag_to_fruit(self,fruit_name:str,tag_name:str) ->Message:
        tag = models.Tag.objects.get(name=tag_name)
        fruit = models.Fruit.objects.get(name=fruit_name)
        try:
            filtre =models.Filter.objects.create(fruit=fruit,tag=tag)
            return Message(success=True,message="Tag ajouter")
        except :
            return Message(success=False,message="Ajout du tag echouer")
        
        
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_color(self, id: int) -> Message:
        try:
            color = models.Color.objects.get(pk=id)
            color.delete()
            return Message(success=True,message="Color deleted successfully")
        except models.Color.DoesNotExist:
            return Message(success=False,message="Color not found")

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_tag(self, id: int, name: str) -> Message:
        try:
            tag = models.Tag.objects.get(pk=id)
            tag.name = name
            tag.save()
            return Message(success=True, message="Tag updated successfully")
        except models.Tag.DoesNotExist:
            return Message(success=False, message="Tag not found")
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_color_name(self, id: int, name: str) -> Message:
        try:
            color = models.Color.objects.get(pk=id)
            color.name = name
            color.save()
            return Message(success=True, message="Color updated successfully")
        except models.Color.DoesNotExist:
            return Message(success=False, message="Color not found")
        
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_color_hexcode(self, id: int, hexval: str) -> Message:
        try:
            color = models.Color.objects.get(pk=id)
            color.hexCode = hexval
            color.save()
            return Message(success=True, message="Color updated successfully")
        except models.Color.DoesNotExist:
            return Message(success=False, message="Color not found")  
        
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_fruit(self, id: int, name: str,description:str=None) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=id)
            if fruit.name == name and fruit.description == description:
                return Message(success=False, message="No changes detected")
            if fruit.name != name:
                fruit.name = name
            if fruit.description != description:
                fruit.description = description
            fruit.save()
            return Message(success=True, message="Fruit updated successfully")
        except models.Fruit.DoesNotExist:
            return Message(success=False, message="Fruit not found")
        except Exception as e:
            if "(name)" in str(e):
                return Message(success=False, message="Fruit with this name already exists")
            return Message(success=False, message=str(e))
            
        
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def remove_tag(self, fruit_id: int, tag_id: int) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=fruit_id)
            tag = models.Tag.objects.get(id=tag_id)
            filtre = models.Filter.objects.get(fruit=fruit,tag=tag)
            filtre.delete()
            return Message(success=True, message="Tag removed successfully")
        except models.Filter.DoesNotExist:
            return Message(success=False, message="Tag not found for this object")
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_fruit(self, id: int) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=id)
            fruit.delete()
            return Message(success=True,message="Fruit deleted successfully")
        except models.Fruit.DoesNotExist:
            return Message(success=False,message="Fruit not found")
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def delete_tag(self,id:int) -> Message:
        try:
            tag = models.Tag.objects.get(pk=id)
            tag.delete()
            return Message(success=True,message="Tag deleted successfully")
        except models.Tag.DoesNotExist:
            return Message(success=False,message="Tag not found")
        
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def update_fruit_image(self,id:int,image:Upload) -> Message:
        try:
            fruit = models.Fruit.objects.get(pk=id)
            #delete old image
            if fruit.image:
                fruit.image.delete()
            fruit.image.save(image.name, image, save=True)
            return Message(success=True,message="Image updated successfully")
        except models.Fruit.DoesNotExist:
            return Message(success=False,message="Fruit not found")    
    
schema = JwtSchema(query=Query, mutation=Mutation)
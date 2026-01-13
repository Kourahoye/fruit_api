from django.db import models
from  django.db.models.constraints import UniqueConstraint
class Fruit(models.Model):

    name = models.CharField(
        max_length=20,
        unique=True,
        null=False,
        blank=False,
        help_text="Nom du fruit"
    )
    color = models.ForeignKey(
        "Color",
        on_delete=models.CASCADE,
        related_name="fruits",
        blank=True,
        null=True,
    )
    description = models.TextField()
    
    tags = models.ManyToManyField(
    'Tag',
    through="Filter",
    )
    
    image = models.ImageField( upload_to="fruits/",max_length=100,null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

class Color(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        max_length=20,
        help_text="couleur du fruits",
    )
    hexCode = models.CharField(
        max_length=7,
        help_text="Code hexadécimal de la couleur",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

class Tag(models.Model):
    name= models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=30,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)
    
class Filter(models.Model):
    fruit = models.ForeignKey('Fruit', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    class Meta:
        constraints =[
            UniqueConstraint(fields=['fruit', 'tag'], name='unique_tag_by_fruit',violation_error_message="Le fruit a deja ce tag")
        ]
    
    def __str__(self):
        return f"Relation {self.fruit.name} et {self.tag.name}"
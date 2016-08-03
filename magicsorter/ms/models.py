from django.db import models

from django.forms import ModelForm
from django.views.generic import ListView
from django.views.generic import DetailView

# Create your models here.
class Card(models.Model):
    image = models.ImageField(upload_to='cards')
    thumb = models.ImageField(upload_to='thumbs')
    hist = models.TextField(blank=True)
    #hist = cv2.calcHist([img],[0],None,[256],[0,256])
     
    name = models.CharField(max_length=255, blank=True)
    price = models.FloatField(blank=True, default=0)
    
    count = models.IntegerField(blank=True, default=0)
    outbox = models.IntegerField(blank=True, default=0)
    
    mtgcode =  models.IntegerField(null=True)
    rarity = models.CharField(max_length=255)
    

    
class CardForm(ModelForm):
    class Meta:
        model = Card
        fields = ['image', 'thumb', 'name', 'price', 'count', 'outbox', 'mtgcode', 'rarity']

    
class Scan(models.Model):
    position = models.IntegerField(blank=True, default=0)
    fk_card = models.ForeignKey(Card)
    outbox = models.IntegerField(blank=True, default=0)
    
    #result0 = models.FloatField(blank=True, default=0)
    #result1 = models.FloatField(blank=True, default=0)
    
    image = models.ImageField(upload_to='scans', blank=True)
    
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=Card)
def card_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)
    instance.thumb.delete(False)

@receiver(pre_delete, sender=Scan)
def scan_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.image.delete(False)
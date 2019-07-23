from django.db import models



class Img(models.Model):
    picture=models.ImageField(default="static/images/placeholder.png")

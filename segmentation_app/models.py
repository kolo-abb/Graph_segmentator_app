from django.db import models



class Img(models.Model):
    picture=models.ImageField(default="static/images/placeholder.png")

class analysis(models.Model):
    name=models.CharField(max_length=100)

class segmentation_analysis(analysis):
    image=Img()


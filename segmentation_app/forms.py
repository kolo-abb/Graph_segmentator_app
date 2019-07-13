from PIL import Image
from django import forms


class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()

# class ImageForm(forms.ModelForm):
#     class Meta:
#         model= Image
#         fields= ["name", "imagefile"]

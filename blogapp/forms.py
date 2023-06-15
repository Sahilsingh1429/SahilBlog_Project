from django.forms import ModelForm
from .models import *
class UserForm(ModelForm):
    class Meta:
        model = User
        # fields = ('first_name','last_name','usernam','email','password')
        exclude  = ('pic','gender')
        
        
        
class BlogForm(ModelForm):
    class Meta:
        model = Blog
        # fields = '__all__'
        exclude = ('user',)
     
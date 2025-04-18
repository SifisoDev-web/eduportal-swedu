from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

 
class Occupation(models.Model):
    USER_TYPE_Occupations = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    user = models.CharField(max_length=250, unique=True)
    type = models.CharField(max_length=10, choices=USER_TYPE_Occupations)

    def __str__(self):
        return self.user + '  :' + self.type

    
  




class TestBase(models.Model):
    Question = models.CharField(max_length=250, unique=True)
    Option1 = models.CharField(max_length=250)
    Option2 = models.CharField(max_length=250)
    Option3 = models.CharField(max_length=250)
    Option4 = models.CharField(max_length=250)
    CorrectOption = models.CharField(max_length=250)
    

    class Meta:
        abstract = True

    def __str__(self):
        return self.Question


class testJava(TestBase):
    pass


class testPython(TestBase):
    pass


class testSQL(TestBase):
    pass


class JavaScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)  
    updated_at = models.DateTimeField(auto_now=True)   

    def __str__(self):
        return f"{self.user.username} - Java Class Score: {self.score}"
    
class SQLScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)   
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.user.username} - SQL Class Score: {self.score}"    

class PythonScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)   
    updated_at = models.DateTimeField(auto_now=True)   
    def __str__(self):
        return f"{self.user.username} - Python Class Score: {self.score}"        

class announc(models.Model):
    contect =models.TextField()
    time    =models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.contect
    

 

class PythonVideo(models.Model):
    title = models.TextField()
    video_file = models.FileField(upload_to='python_videos/%y')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SQLVideo(models.Model):
    title = models.TextField()
    video_file = models.FileField(upload_to='SQL_videos/%y')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JavaVideo(models.Model):
    title = models.TextField()
    video_file = models.FileField(upload_to='java_videos/%y')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models

class Question(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()

    def __str__(self):
        return self.subject

class Answer(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()

class Finance(models.Model):
    Date= models.DateTimeField()
    Open = models.FloatField()
    High = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    Volume = models.FloatField()
    Change = models.FloatField()

#코스피
class Kospi(models.Model):
    Symbol = models.IntegerField()
    Market = models.TextField()
    Name = models.TextField()

#코스닥
class Kosdaq(models.Model):
    Symbol = models.IntegerField()
    Market = models.TextField()
    Name = models.TextField()

#리스크
class Risk(models.Model):
    spread = models.FloatField()
    DXY = models.FloatField()
    Label = models.IntegerField()
    Date = models.TextField()


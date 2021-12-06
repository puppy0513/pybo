from django.contrib import admin
from .models import Question , Finance, Risk, Kospi



class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']

class FinanceAdmin(admin.ModelAdmin):
    search_fields = ['Open']

class RiskAdmin(admin.ModelAdmin):
    search_fields = ['Date']

class KospiAdmin(admin.ModelAdmin):
    search_fields = ['Name']

admin.site.register(Finance,FinanceAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Risk,RiskAdmin)
admin.site.register(Kospi,KospiAdmin)
# Register your models here.

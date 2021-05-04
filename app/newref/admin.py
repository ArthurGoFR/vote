from django.contrib import admin
from .models import Ref, Question, Option, Rawvote, Touralter
# Register your models here.

admin.site.register(Ref)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Rawvote)
admin.site.register(Touralter)
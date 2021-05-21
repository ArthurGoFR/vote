from django.db import models
from django.forms import ModelForm, Textarea, RadioSelect, HiddenInput, DateInput, SelectDateWidget, TimeInput
from django import forms
from django.conf import settings
import datetime
from django.utils import timezone

from django.forms.fields import FileField


class DateInput(DateInput):
    input_type = 'date'

DEP_CHOICES = [

    ('CLASSIC', "Choix : Sélection d'une option - Comptabilisation : Classique"),
    ('ALT', "(En construction) Choix Hiérarchisation des options - Comptabilisation : vote alternatif"),
    ('JUG', "(En construction) Jugement majoritaire "),
    ]

STATUS_CHOICES = [
    ('CONFIG', "En cours de configuration"),
    ('RUN', 'Bulletins envoyés - En cours de vote'),
    ('FINISHED', 'Les résultats sont disponibles'),
]

jugoptions = {1:"Excellent", 2:"Bien", 3:"Bof", 4:"Nul", 5:"Rejet"}

class Ref(models.Model):
    text = models.CharField(max_length=1000)
    bulletin_text = models.CharField(max_length=1000, default="Vous êtes invité.e à voter. Attention à ne pas partager ce bulletin : les personnes qui y accéderont pourront voter à votre place.")
    bulletin_img = models.CharField(max_length=300, default="https://www.batiactu.com/images/auto/620-465-c/20200311_170654_39186406illustration-wissanu99.jpg")
    bulletin_objet = models.CharField(max_length=300, default="Votre bulletin de vote")
    start = models.DateField(blank=True, null=True, default=datetime.date.today())
    end = models.DateField(blank=True, null=True, default=datetime.date.today()+datetime.timedelta(days=7))

    start_time = models.TimeField(blank=True, null=True, default=datetime.datetime.now())
    end_time = models.TimeField(blank=True, null=True, default= datetime.time(16, 00))

    depouillement = models.CharField(max_length=10, choices=DEP_CHOICES, default="CLASSIC")
    jugoptions = models.JSONField(default=jugoptions)
    secret_key = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CONFIG")
    
    crypted = models.BooleanField(default=True)
    public_key = models.FileField(upload_to='public_keys/', blank=True, null=True)
    private_key = models.FileField(upload_to='private_keys/', blank=True, null=True)
    crypted_email_host_password = models.BinaryField(max_length=3000, blank=True, null=True)

    email_use_tls = models.BooleanField(default=False)
    email_host = models.CharField(max_length=300, blank=True, null=True)
    email_host_user = models.CharField(max_length=100, blank=True, null=True)
    email_host_password = models.CharField(max_length=100, blank=True, null=True)
    email_port = models.IntegerField(max_length=300, blank=True, null=True)

class RefForm(ModelForm):

    start = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',  attrs={'type': 'date'}),
        input_formats=('%Y-%m-%d', ),
        label="Quel jour commence la votation :",
        required=True
        )

    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M',  attrs={'type': 'time'}),
        # input_formats=('%Y-%m-%d', ),
        label="A quelle heure :",
        required=True
        )

    end = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',  attrs={'type': 'date',}),
        input_formats=('%Y-%m-%d', ),
        label="Quelle jour se termine la votation :",
        required=True
        )

    end_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M',  attrs={'type': 'time'}),
        # input_formats=('%Y-%m-%d', ),
        label="A quelle heure :",
        required=True
        )

    class Meta:
        model = Ref
        fields = ['text','start','start_time','end','end_time','depouillement']
        widgets = {
            # # 'start': DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
            # 'end_time': TimeInput(format='%H:%M'),
            # 'text':Textarea(attrs={'cols': 80, 'rows': 5})
    
        }
        labels = {
            'text': 'Le titre de la votation :',
            'bulletin_text': 'Le texte qui apparaitra sur les bulletins en plus du titre :',
            'depouillement':"Le type de vote & La manière de comptabiliser :"
        }


class SmallRefForm(ModelForm):
    class Meta:
        model = Ref
        fields = ['text','secret_key','crypted']

        labels = {
            'text': 'Entrer un nom provisoire pour votre votation',
            'secret_key': "Entrer un code secret pour votre votation. Attention à ne pas le perdre, il sera nécessaire pour revenir à l'administration !",
            'crypted': "Encrypter les données sensibles (mot de passe de la boite mail d'envoi, bulletins envoyés) (recommandé) ?"
        }


class BulletinRefForm(ModelForm):
    class Meta:
        model = Ref
        fields = ['bulletin_text','bulletin_img','bulletin_objet',
         'email_host', 'email_port', 'email_host_user','email_host_password','email_use_tls',]

        labels = {
            'bulletin_text': 'Un texte qui va apparaitre sur le bulletin',
            'bulletin_img': "Un lien vers l'image qui apparaitra sur le bulletin",
            'email_host': "Serveur SMTP pour l'envoi des bulletins",
            'email_port': "Port",
            'email_host_user': "Nom d'utilisateur",
            'email_host_password': "Mot de passe",
            'email_use_tls': "TLS",
        }        


class Question(models.Model):
    text = models.CharField(max_length=1000)
    ref =  models.ForeignKey(Ref, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['text']

        widgets = {
        }
        labels = {
            'text': 'Intitulé de la question :',
        }

class Option(models.Model):
    text = models.CharField(max_length=1000)
    question =  models.ForeignKey(Question, on_delete=models.CASCADE)

class OptionForm(ModelForm):
    class Meta:
        model = Option
        fields = ["question",'text']

        labels = {
            'text': "Intitulé de l'option :",
            'question': 'Question associée:',
        }

    def __init__(self, ref, *args, **kwargs):
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields['question'].queryset = Question.objects.filter(ref=ref)

STAT_CHOICES = [
    ('INIT', "Statut initial"),
    ('SENT', "Bulletin envoyé"),
    ('STUCK', "Vote arrêté")
    ]

class Rawvote(models.Model):
    ref = models.ForeignKey(Ref, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    code = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STAT_CHOICES, default="INIT")
    json = models.JSONField(max_length=1000, blank=True, null=True)
    crypted_json = models.BinaryField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.email

class RawvoteForm(ModelForm):
    class Meta:
        model = Rawvote
        fields = ['code', 'json']
        widgets = {'code': HiddenInput(), 'json': HiddenInput()}

class Touralter(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    results = models.JSONField()
    num = models.IntegerField(blank=True, null=True)
    removed_option = models.ForeignKey(Option, on_delete=models.CASCADE, blank=True, null=True)
    
class Tour(models.Model):
    ref = models.ForeignKey(Ref, on_delete=models.CASCADE)
    results = models.JSONField()
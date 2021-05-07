from django.db import models
from django.forms import ModelForm, Textarea, RadioSelect, HiddenInput, DateInput, SelectDateWidget
from django import forms
from django.conf import settings

class DateInput(DateInput):
    input_type = 'date'

DEP_CHOICES = [
    ('ALT', "Choix : Hiérarchisation des options (par Drag & Drop) - Comptabilisation : vote alternatif"),
    ('CLASSIC', "Choix : Sélection d'une option - Comptabilisation : Classique"),
    ]

STATUS_CHOICES = [
    ('CONFIG', "En cours de configuration"),
    ('RUN', 'Bulletins envoyés - En cours de vote'),
    ('FINISHED', 'Les résultats sont disponibles'),
]


class Ref(models.Model):
    text = models.CharField(max_length=1000)
    bulletin_text = models.CharField(max_length=1000, blank=True, null=True, default="Vous êtes invité.e à voter. Attention à ne pas partager ce bulletin : les personnes qui y accéderont pourront voter à votre place.")
    bulletin_img = models.CharField(max_length=300, blank=True, null=True, default="https://www.batiactu.com/images/auto/620-465-c/20200311_170654_39186406illustration-wissanu99.jpg")
    bulletin_objet = models.CharField(max_length=300, blank=True, null=True, default="Votre bulletin de vote")
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    depouillement = models.CharField(max_length=10, choices=DEP_CHOICES, default="ALT")
    secret_key = models.CharField(max_length=100)
    hash = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CONFIG")

    email_use_tls = models.BooleanField(default=False)
    email_host = models.CharField(max_length=300, blank=True, null=True)
    email_host_user = models.CharField(max_length=100, blank=True, null=True)
    email_host_password = models.CharField(max_length=100, blank=True, null=True)
    email_port = models.IntegerField(max_length=300, blank=True, null=True)

class RefForm(ModelForm):

    start = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',  attrs={'type': 'date'}),
        input_formats=('%Y-%m-%d', ),
        label="Quand commence la votation (début à 0:01)",
        required=False
        )

    end = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d',  attrs={'type': 'date',}),
        input_formats=('%Y-%m-%d', ),
        label="Quand se termine la votation (fin à 23:59) :",
        required=False
        )

    class Meta:
        model = Ref
        fields = ['text', 'start','end','depouillement']
        widgets = {
            # 'start': DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
            # 'end': DateInput(),
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
        fields = ['text','secret_key']

        labels = {
            'text': 'Entrer un nom provisoire pour votre votation',
            'secret_key': "Entrer un code secret pour votre votation. Attention à ne pas le perdre, il sera nécessaire pour revenir à l'administration !",
            # 'text': "Une question ? Un message ? (c'est optionnel)"
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
    

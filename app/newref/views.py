from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Ref, Question, QuestionForm, Option, OptionForm, Rawvote, RawvoteForm, Touralter, RefForm, SmallRefForm, BulletinRefForm
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
import pytz
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Count
from django.urls import reverse
from django.conf import settings

def apropos(request):
	return render(request,"newref/apropos.html")

#La page d'accueil où sont tous les refs en cours
def refs(request):
	template="newref/refs.html"
	
	#Si c'est un post, quelqu'un créé une nouvelle votation
	if request.method=="POST":
		form = SmallRefForm(request.POST)
		if form.is_valid():
			ref = form.save(commit=False)
			import hashlib
			ref.hash = hashlib.sha224(bytes(ref.secret_key, encoding="utf-8")).hexdigest()
			ref.save()

			#On créé l'user test pour la preview
			import random
			import string
			letters = string.ascii_lowercase
			code = ''.join(random.choice(letters) for i in range(50))

			rawvote = Rawvote(
				ref = ref,
				email = "test@exemple.fr",
				code= code
			)
			rawvote.save()

			return HttpResponseRedirect(reverse('voteadmin', args = (ref.hash,)))
	
	refs = Ref.objects.all()
	form = SmallRefForm()
	
	context= {"form":form,"refs":refs}
	return render(request, template, context)

#Pour accéder à l'admin d'un ref à partir d'une secret key
def secret_key_check(request):
	if request.method == "POST":
		try:
			ref = Ref.objects.get(secret_key = request.POST["secret_key"])
			return HttpResponseRedirect(reverse('voteadmin', args = (ref.hash,)))
		except:
			return HttpResponseRedirect(reverse('refs'))

	return HttpResponseRedirect(reverse('refs'))

#La page de config de base pour un ref
def voteadmin(request, hash):
	template = "newref/voteadmin.html"
	ref = Ref.objects.get(hash = hash)

	if request.method=="POST":
		form = RefForm(request.POST, instance=ref)
		if form.is_valid():
			ref = form.save()

	form = RefForm(instance=ref)

	context = {"ref":ref, "form":form}
	return render(request, template, context)

#La page de config de des questions et options pour un ref
def voteadmin_questions(request, hash):
	template = "newref/voteadmin_questions.html"
	ref = Ref.objects.get(hash = hash)

	if request.method == "POST":
		print(request.POST)
		try:
			form = OptionForm(ref, request.POST)
			option = form.save()
		except:
			form = QuestionForm(request.POST)
			question = form.save(commit=False)
			question.ref = ref
			question.save()

	ref.questions = Question.objects.filter(ref=ref)
	for question in ref.questions:
		question.options = Option.objects.filter(question = question)

	form = QuestionForm()

	optionForm = OptionForm(ref)

	context = {"ref":ref, "form":form, "optionForm":optionForm}
	return render(request, template, context)

#Pour delete une question
def delete_question(request, hash, id_question):
	question = Question.objects.get(id = id_question)
	if question.ref.hash == hash:
		question.delete()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#Pour delete une option
def delete_option(request, hash, id_option):
	option = Option.objects.get(id = id_option)
	if option.question.ref.hash == hash:
		option.delete()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#La page de config des votants pour un ref
def voteadmin_votants(request, hash):
	template = "newref/voteadmin_votants.html"
	ref = Ref.objects.get(hash = hash)
	msg=None

	if request.method=="POST":

		import csv
		from io import StringIO
		import random
		import string
		import re
		regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

		file = request.FILES['file'] 
		decoded_file = file.read().decode('utf-8')
		reader = csv.reader(StringIO(decoded_file), delimiter=' ', quotechar='|')
		
		created = []
		already_created = []
		not_valid = []

		for row in reader:
			try:		
				email = row[0]

				if re.search(regex, email):
					rawvotes = Rawvote.objects.filter(ref = ref, email = email)

					if rawvotes.count() == 0:
						letters = string.ascii_lowercase
						code = ''.join(random.choice(letters) for i in range(50))
						rawvote = Rawvote()
						rawvote.email = email
						rawvote.code = code
						rawvote.ref = ref 
						rawvote.save()
						created.append(email)
					else:
						already_created.append(email)
				else:
					not_valid.append(email)
			except:
				pass

		msg="<strong>Résultat du traitement de "+request.FILES['file'].name+" : </strong><br/>"
		msg = msg+str(len(created))+" adresses ajoutées<br/>"
		msg = msg+str(len(already_created))+" adresses étaient déjà ajoutées<br/>"
		msg = msg+str(len(not_valid))+" adresses non valides : "+str(not_valid)

	ref.rawvotes = Rawvote.objects.filter(ref = ref).order_by("email").exclude(email="test@exemple.fr")
	
	context = {"ref":ref, "msg":msg }
	return render(request, template, context)
	
#Pour delete un votant
def delete_rawvote(request, hash, id_rawvote):
	rawvote = Rawvote.objects.get(id = id_rawvote)
	if rawvote.ref.hash == hash:
		rawvote.delete()
		return HttpResponseRedirect(reverse('voteadmin_votants', args = (hash,)))

#La page de config pour les bulletins
def voteadmin_bulletins(request, hash):
	template = "newref/voteadmin_bulletins.html"
	ref = Ref.objects.get(hash = hash)
	
	if request.method == "POST":
		form = BulletinRefForm(request.POST, instance = ref)
		if form.is_valid():
			ref = form.save()

	form = BulletinRefForm(instance = ref)
	context = {"ref":ref, "form":form}
	return render(request, template, context)

#Pour générer l'html utilisé pour les bulletins
def generate_html_bulletin(rawvote):
	
	ref = rawvote.ref
	abs_path = "http://"+settings.DOMAIN_NAME
	htmly = get_template('newref/mail_base.html')
	htmly = get_template('newref/mail_base.html')
	text = ref.bulletin_text+"<br/><br/>"
	try:
		text=text+"Début de la votation : le "+str(ref.start.strftime("%d/%m/%Y"))+" à 0:01<br/>"
		text=text+"Fin de la votation : le "+str(ref.end.strftime("%d/%m/%Y"))+" à 23:59<br/>"
	except:
		text=text+"Début de la votation : <br/>"
		text=text+"Fin de la votation : "

	d = { 
		'title': ref.text,
		'text': text,
		'href' : abs_path+str(reverse('votepage', args = (rawvote.code,))),
		'button': "Aller voter",
		'image': ref.bulletin_img
			}

	html = htmly.render(d)
	return html

def generate_backend(ref):
	backend = EmailBackend(
		host=ref.email_host, 
		port=ref.email_port, 
		username=ref.email_host_user, 
		password=ref.email_host_password, 
		use_tls=ref.email_use_tls, 
		fail_silently=False
		)
	return backend

#Pour vérifier que les mails sont bien envoyés
def test_email_sending(request,hash):
	
	ref = Ref.objects.get(hash = hash)
	if request.method=="POST":
		backend = generate_backend(ref)
		destinataires = []
		destinataires.append(request.POST["email"])
		email = EmailMessage(
			subject='Décidons : Test de connexion réussi !', 
			body="Vous avez correctement configuré la boite d'envoi.", 
			from_email=ref.email_host_user, 
			to=destinataires,
            connection=backend
			)
		email.send()
	return HttpResponseRedirect(reverse('voteadmin_bulletins', args = (hash,)))		


#Pour visualiser un bulletin
def preview_bulletin(request, hash):
	ref = Ref.objects.get(hash = hash)
	rawvote = Rawvote.objects.filter(ref=ref).filter(email="test@exemple.fr")[0]
	html = generate_html_bulletin(rawvote)
	return HttpResponse(html)

#Pour envoyer un bulletin par mail
def mail_bulletin(rawvote):
	
	html = generate_html_bulletin(rawvote)
	backend = generate_backend(rawvote.ref)

	subject = rawvote.ref.bulletin_objet
	from_email = rawvote.ref.email_host_user
	destinataires = [rawvote.email]
	text_content = 'Les informations sont dans la version HTML'
	html_content = html

	msg = EmailMultiAlternatives(
		subject=subject, 
		body=text_content,
		from_email=from_email,
		to= destinataires,
		connection=backend
		)
	msg.attach_alternative(html_content, "text/html")
	try:
		msg.send()
		rawvote.status="SENT"
		rawvote.save()
	except:
		pass

#Pour envoyer tous les bulletins (et passer le ref en RUN)
def send_bulletins(request, hash):
	ref = Ref.objects.get(hash = hash)
	rawvotes = Rawvote.objects.filter(ref = ref).exclude(email="test@exemple.fr")
	for rawvote in rawvotes:
		mail_bulletin(rawvote)
	ref.status = "RUN"
	ref.save()
	return HttpResponseRedirect(reverse('voteadmin_bulletins', args = (hash,)))


#Page de vote
def votepage(request, code):
	template = "newref/votepage_alter.html"
	rawvote = Rawvote.objects.get(code = code)
	ref = rawvote.ref
	ref.questions = Question.objects.filter(ref = ref)

	if request.method=="POST":
		form = RawvoteForm(request.POST, instance=rawvote)
		if form.is_valid():
			rawvote = form.save()

	for question in ref.questions:
		question.options = Option.objects.filter(question = question)
		try:
			question.order = rawvote.json[str(question.id)]
		except:
			question.order = []

	form = RawvoteForm(instance = rawvote)

	context = {"ref":ref, 'form':form, 'rawvote':rawvote}
	return render(request, template, context)

def votedelete(request, code):

	rawvote = Rawvote.objects.get(code = code)
	rawvote.json = None
	rawvote.save()
	return HttpResponseRedirect(reverse('votepage', args = (code,)))



#Pour gérer le dépouillement
def voteadmin_depouillement(request, hash):
	template = "newref/voteadmin_depouillement.html"
	ref = Ref.objects.get(hash = hash)
	
	today=datetime.date(datetime.today())
	
	try:
		if today<ref.start:
			ref.when = "before"
		elif today<=ref.end:
			ref.when = "during"
		else:
			ref.when = "after"
	except:
		ref.when = "before"
	
	ref.valid_rawvotes = Rawvote.objects.filter(ref = ref).filter(json__isnull=False)
	context = {"ref":ref}
	return render(request, template, context)

#Ce qu'on envoie pour lancer le dépouillement
def ref_depouillement(request, hash):
	ref = Ref.objects.get(hash=hash)
	if ref.depouillement == "ALT":
		trait_alter(ref)
		ref.status="FINISHED"
		ref.save()
	return HttpResponseRedirect(reverse('voteadmin_depouillement', args = (hash,)))


#Fonction qui calcul les résultats pour un vote alternatif
def trait_alter(ref):
	questions = Question.objects.filter(ref = ref)
	valid_rawvotes = Rawvote.objects.filter(ref = ref).exclude(json__isnull=True)
	Touralter.objects.filter(question__in=questions).delete()
	
	for question in questions:
		options = Option.objects.filter(question = question)
		num = 1
		while num < options.count():
		
			touralter = Touralter()
			touralter.question = question
			touralter.num = num
			results = {}
			for option in options:
				results[option.id] = 0

			touralters = Touralter.objects.filter(question = question)
			for valid_rawvote in valid_rawvotes:
				for old_touralter in touralters:
					valid_rawvote.json[str(question.id)].remove(str(old_touralter.removed_option.id))

				pref_o = valid_rawvote.json[str(question.id)][0]
				results[int(pref_o)] += 1

			touralter.results = results
			touralter.removed_option = Option.objects.get(id=min(results, key=results.get))

			touralter.save()
			num += 1
	

def fakevotes(id_ref):

	import random
	import string
	letters = string.ascii_lowercase

	ref = Ref.objects.get(id=id_ref)
	Rawvote.objects.filter(ref=ref).delete()

	for i in range(100):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"1": ["1", "2", "3"], "2": ["5", "4"]}
		rawvote.save()

	for i in range(90):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"1": ["2", "3", "1"], "2": ["4", "5"]}
		rawvote.save()

	for i in range(80):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"1": ["3", "1", "2"], "2": ["4", "5"]}
		rawvote.save()

#Afficher les résultats des votes alternatifs
def ref_results(request, id_ref):
	template = "newref/voteresults.html" 

	ref = Ref.objects.get(id = id_ref)
	ref.questions = Question.objects.filter(ref = ref)
	for question in ref.questions:
		question.touralters = Touralter.objects.filter(question=question)
		question.options = Option.objects.filter(question = question)	
		
		for option in question.options:
			option.horizontal_results = {}
			for touralter in question.touralters:
				option.horizontal_results[touralter.num] = touralter.results[str(option.id)]

		# for option in question.options:
		# 	option.value = {}
		# 	for touralter in touralters:
		# 		option.value[touralter.num] = touralter.results[str(option.id)]

	context = {"ref": ref}
	return render(request, template, context)

def communicate_results(request, hash):
	a=1
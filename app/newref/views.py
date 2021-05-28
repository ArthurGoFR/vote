from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .models import Ref, Question, QuestionForm, Option, OptionForm, OptionFormSimple, Rawvote, RawvoteForm, Touralter, Tour, RefForm, SmallRefForm, BulletinRefForm
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
import time
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
from django.core import serializers
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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

			if ref.crypted:				
				key = RSA.generate(2048)
				private_key = key.export_key()
				file_out = open("mediafiles/clef_votation_a_garder_precieusement_"+str(ref.id)+".pem", "wb")
				file_out.write(private_key)
				file_out.close()
				ref.private_key = "clef_votation_a_garder_precieusement_"+str(ref.id)+".pem"
				
				public_key = key.publickey().export_key()
				file_out = open("mediafiles/public_key_"+str(ref.id)+".pem", "wb")
				file_out.write(public_key)
				file_out.close()
				ref.public_key = "public_key_"+str(ref.id)+".pem"
				
				ref.save()
				
				return HttpResponseRedirect(reverse('rsa_display', args = (ref.hash,)))

			return HttpResponseRedirect(reverse('voteadmin', args = (ref.hash,)))
	
	refs = Ref.objects.all()
	form = SmallRefForm()
	
	context= {"form":form,"refs":refs}
	return render(request, template, context)

def rsa_display(request, hash):
	ref = Ref.objects.get(hash = hash)
	template="newref/rsa_display.html"
	context = {"ref":ref}
	return render(request, template, context)

def rsa_delete(request,hash):
	ref = Ref.objects.get(hash=hash)
	ref.private_key.delete()
	ref.save()
	return HttpResponseRedirect(reverse('rsa_display', args = (ref.hash,)))	

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

	import json
	if request.method=="POST":
		form = RefForm(request.POST, instance=ref)
		if form.is_valid():
			ref = form.save()
			raw = Rawvote.objects.get(ref = ref, email = "test@exemple.fr")
			raw.json = None
			raw.save()
			# json_raw = serializers.serialize("json", [raw,])
			return JsonResponse({'success': True})
			# return JsonResponse({"success" : True})
	# if request.method=="POST":
	# 	print("dada")
	# 	# print(form)
	# 	# form = RefForm(request.POST, instance=ref)
		

	form = RefForm(instance=ref)

	context = {"ref":ref, "form":form}
	return render(request, template, context)

#La page de config de des questions et options pour un ref
def voteadmin_questions(request, hash):
	template = "newref/voteadmin_questions.html"
	ref = Ref.objects.get(hash = hash)

	if request.method == "POST":
		try:
			form = OptionForm(ref, request.POST)
			option = form.save(commit=False)
			other_options_count = Option.objects.filter(question=option.question).count()
			option.order = other_options_count+1
			option.save()
		except:
			form = QuestionForm(request.POST)
			question = form.save(commit=False)
			question.ref = ref
			other_questions_count = Question.objects.filter(ref=ref).count()
			question.order = other_questions_count+1
			question.save()

	ref.questions = Question.objects.filter(ref=ref).order_by('order')
	for question in ref.questions:
		question.options = Option.objects.filter(question = question).order_by('order')

	form = QuestionForm()
	optionForm = OptionForm(ref)

	ref.testvote = Rawvote.objects.get(ref=ref, email="test@exemple.fr")

	context = {"ref":ref, "form":form, "optionForm":optionForm}
	return render(request, template, context)

#Pour delete une question
def delete_question(request, hash, id_question):
	question = Question.objects.get(id = id_question)
	if question.ref.hash == hash:
		questions_after = Question.objects.filter(ref=question.ref).filter(order__gt = question.order)
		for question_after in questions_after:
			question_after.order = question_after.order - 1
			question_after.save()
		question.delete()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#Pour moveup une question
def moveup_question(request, hash, id_question):
	question = Question.objects.get(id = id_question)
	if question.ref.hash == hash:
		if question.order > 1:
			other_question = Question.objects.filter(ref=question.ref).filter(order=question.order-1).first()
			other_question.order=other_question.order+1
			question.order = question.order-1
			other_question.save()
			question.save()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#Pour moveup une option
def moveup_option(request, hash, id_option):
	option = Option.objects.get(id = id_option)
	if option.question.ref.hash == hash:
		if option.order > 1:
			other_option = Option.objects.filter(question=option.question).filter(order=option.order-1).first()
			other_option.order=other_option.order+1
			option.order = option.order-1
			other_option.save()
			option.save()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#Pour delete une option
def delete_option(request, hash, id_option):
	option = Option.objects.get(id = id_option)
	if option.question.ref.hash == hash:
		options_after = Option.objects.filter(order__gt = option.order).filter(question = option.question)
		for option_after in options_after:
			option_after.order = option_after.order - 1
			option_after.save()
		option.delete()
		return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))

#Pour edit une question
def edit_question(request, hash, id_question):
	question = Question.objects.get(id = id_question)
	if question.ref.hash == hash:
		if request.method == "POST":
			form = QuestionForm(request.POST, instance=question)
			if form.is_valid():
				form.save()
			return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))
	
		form = QuestionForm(instance = question)
		template = "newref/edit_question.html"
		context = {"question":question,"form":form}	
		return render(request, template, context)

#Pour moveup une option
def edit_option(request, hash, id_option):
	option = Option.objects.get(id = id_option)
	if option.question.ref.hash == hash:
		if request.method == "POST":
			form = OptionFormSimple(request.POST, instance=option)
			if form.is_valid():
				form.save()
			return HttpResponseRedirect(reverse('voteadmin_questions', args = (hash,)))
	
		
		form = OptionFormSimple(instance = option)
		template = "newref/edit_option.html"
		context = {"option":option,"form":form}	
		return render(request, template, context)

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
	ref = Ref.objects.get(hash=hash)
	rawvote = Rawvote.objects.get(id = id_rawvote)
	if rawvote.ref == ref and ref.status == "CONFIG":
		rawvote.delete()
	return HttpResponseRedirect(reverse('voteadmin_votants', args = (hash,)))

#Pour delete tous les votants:
def delete_all_rawvotes(request, hash):
	ref = Ref.objects.get(hash=hash)
	if ref.status == "CONFIG":
		Rawvote.objects.filter(ref=ref).exclude(email="test@exemple.fr").delete()
	return HttpResponseRedirect(reverse('voteadmin_votants', args = (hash,)))

#La page de config pour les bulletins
def voteadmin_bulletins(request, hash):
	template = "newref/voteadmin_bulletins.html"
	ref = Ref.objects.get(hash = hash)
	
	if ref.status != "CONFIG":
		ref.sent_rawvotes = Rawvote.objects.filter(ref=ref).filter(status="SENT").exclude(email="test@exemple.fr")
		ref.unsent_rawvotes = Rawvote.objects.filter(ref=ref).filter(status="INIT").exclude(email="test@exemple.fr")
		ref.failsent_rawvotes = Rawvote.objects.filter(ref=ref).filter(status="FAIL").exclude(email="test@exemple.fr")

	if request.method == "POST":
		form = BulletinRefForm(request.POST, instance = ref)
		
		#Pour les nons cryptés
		if form.is_valid() and not ref.crypted:
			ref.save()
			return JsonResponse({'success': True})

		#Pour les refs cryptés
		if form.is_valid() and ref.crypted:
			try:
				crypted_password = ref.crypted_email_host_password
			except:
				crypted_password = None

			ref.save()

			ref.crypted_email_host_password = None
			#Quand c'est la valeur par défaut qui est envoyée, remettre le vrai mot de passe
			if ref.email_host_password == "donotchange":
				ref.crypted_email_host_password = crypted_password
			elif ref.email_host_password:
				cipher = PKCS1_OAEP.new(RSA.importKey(ref.public_key.read()))
				ref.crypted_email_host_password = cipher.encrypt(ref.email_host_password.encode("utf-8"))
			#On efface le mot de passe en clair
			ref.email_host_password = None
			ref.save()  

			return JsonResponse({'success': True})

	form = BulletinRefForm(instance = ref)
	context = {"ref":ref, "form":form}
	return render(request, template, context)

#Pour générer l'html utilisé pour les bulletins
def generate_html_bulletin(rawvote):
	
	ref = rawvote.ref
	abs_path = "http://"+settings.DOMAIN_NAME
	htmly = get_template('newref/mail_base.html')
	text = ref.bulletin_text+"<br/><br/>"
	try:
		text=text+"Début de la votation : le "+str(ref.start.strftime("%d/%m/%Y"))+" à "+str(ref.start_time.strftime("%H:%M"))+"<br/>"
		text=text+"Fin de la votation : le "+str(ref.end.strftime("%d/%m/%Y"))+" à "+str(ref.end_time.strftime("%H:%M"))+"<br/>"
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

def generate_backend(ref, private_key=None):
	
	if ref.crypted:
		cipher = PKCS1_OAEP.new(RSA.importKey(private_key.read()))
		password = cipher.decrypt(ref.crypted_email_host_password).decode("utf-8")
	else:
		password = ref.email_host_password

	backend = EmailBackend(
		host=ref.email_host, 
		port=ref.email_port, 
		username=ref.email_host_user, 
		password=password, 
		use_tls=ref.email_use_tls, 
		fail_silently=False
		)
	return backend

#Pour vérifier que les mails sont bien envoyés
def test_email_sending(request,hash):
	ref = Ref.objects.get(hash = hash)
	if request.method=="POST":
		
		try:
			if ref.crypted:
				backend = generate_backend(ref, request.FILES["private_key"])
			else:
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
			return JsonResponse({"success" : True})
		except:
			return JsonResponse({"success" : False})
	return HttpResponseRedirect(reverse('voteadmin_bulletins', args = (hash,)))		


#Pour visualiser un bulletin
def preview_bulletin(request, hash):
	ref = Ref.objects.get(hash = hash)
	rawvote = Rawvote.objects.filter(ref=ref).filter(email="test@exemple.fr")[0]
	html = generate_html_bulletin(rawvote)
	return HttpResponse(html)

#Pour envoyer un bulletin par mail
def mail_bulletin(rawvote, backend, private_key=None):
	
	html = generate_html_bulletin(rawvote)
	# backend = generate_backend(rawvote.ref)

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
		rawvote.status="FAIL"
		rawvote.save()

#Pour envoyer tous les bulletins (et passer le ref en RUN)
def send_bulletins(request, hash):
	if request.method=="POST":
		ref = Ref.objects.get(hash = hash)
		if ref.crypted:
			if ref.crypted_email_host_password:
				backend = generate_backend(ref, request.FILES["private_key"])
			else:
				return HttpResponseRedirect(reverse('voteadmin_bulletins', args = (hash,)))
		else:
			backend = generate_backend(ref)

		print("sélection des rawvotes")
		rawvotes = Rawvote.objects.filter(ref = ref).filter(status = "INIT").exclude(email="test@exemple.fr")			
		print("Envoi...")
		for rawvote in rawvotes:
			try:
				mail_bulletin(rawvote, backend)
				time.sleep(0.3)
			except:
				print("échec : "+str(rawvote.email))
			
		# mail_bulletin(rawvotes[0], backend)
		ref.status = "RUN"
		ref.save()
	return HttpResponseRedirect(reverse('voteadmin_bulletins', args = (hash,)))

def not_received_bul(request, hash, id_rawvote):
	ref = Ref.objects.get(hash=hash)
	rawvote = Rawvote.objects.get(id=id_rawvote)
	if rawvote.ref == ref:
		rawvote.status = "INIT"
		rawvote.save()
	return HttpResponseRedirect(reverse('voteadmin_votants', args = (rawvote.ref.hash,)))

#Page de vote
def votepage(request, code):
	
	rawvote = Rawvote.objects.get(code = code)
	ref = rawvote.ref
	ref.when = when_ref(ref)
	ref.questions = Question.objects.filter(ref = ref).order_by('order')

	if request.method=="POST":
		form = RawvoteForm(request.POST, instance=rawvote)
		if form.is_valid() and ref.when == "during":
			rawvote = form.save()
			if ref.crypted:
				cipher = PKCS1_OAEP.new(RSA.importKey(rawvote.ref.public_key.read()))
				rawvote.crypted_json = cipher.encrypt(str(rawvote.json).encode("utf-8"))
				rawvote.json=None
				rawvote.save()

	if ref.depouillement == "ALT":
		template = "newref/votepage_alter.html"
		for question in ref.questions:
			question.options = Option.objects.filter(question = question)
			try:
				question.order = rawvote.json[str(question.id)]
			except:
				question.order = []

	elif ref.depouillement == "CLASSIC":
		template = "newref/votepage_classic.html"
		for question in ref.questions:
			question.options = Option.objects.filter(question = question).order_by('order')

	elif ref.depouillement == "JUG":
		template = "newref/votepage_jug.html"
		ref.low_option = list(ref.jugoptions.keys())[-1]
		for question in ref.questions:
			question.options = Option.objects.filter(question = question)

	form = RawvoteForm(instance = rawvote)

	context = {"ref":ref, 'form':form, 'rawvote':rawvote}
	return render(request, template, context)

def votedelete(request, code):

	rawvote = Rawvote.objects.get(code = code)
	rawvote.json = None
	rawvote.crypted_json = None
	rawvote.save()
	return HttpResponseRedirect(reverse('votepage', args = (code,)))


#Où en est on par rapport à la date de vote
def when_ref(ref):
	now=datetime.now()
	start=datetime.combine(ref.start, ref.start_time)
	end=datetime.combine(ref.end, ref.end_time)
	try:
		if now<start:
			when = "before"
		elif now<end:
			when = "during"
		else:
			when = "after"
	except:
		when = "before"
	return when

#Pour gérer le dépouillement
def voteadmin_depouillement(request, hash):
	template = "newref/voteadmin_depouillement.html"
	ref = Ref.objects.get(hash = hash)
	ref.when = when_ref(ref)

	if ref.crypted:
		ref.valid_rawvotes = Rawvote.objects.filter(ref = ref).filter(crypted_json__isnull=False).exclude(email="test@exemple.fr")
		ref.sent_rawvotes = Rawvote.objects.filter(ref=ref).exclude(status="INIT").exclude(email="test@exemple.fr")	
	else:
		ref.valid_rawvotes = Rawvote.objects.filter(ref = ref).filter(json__isnull=False).exclude(email="test@exemple.fr")
		ref.sent_rawvotes = Rawvote.objects.filter(ref=ref).exclude(status="INIT").exclude(email="test@exemple.fr")

	context = {"ref":ref}
	return render(request, template, context)

def voteadmin_depouillement_anticipe(request, hash):
	template = "newref/voteadmin_depouillement.html"
	ref = Ref.objects.get(hash = hash)
	
	ref.when = "after"
	
	if ref.crypted:
		ref.valid_rawvotes = Rawvote.objects.filter(ref = ref).filter(crypted_json__isnull=False).exclude(email="test@exemple.fr")
		ref.sent_rawvotes = Rawvote.objects.filter(ref=ref).exclude(status="INIT").exclude(email="test@exemple.fr")	
	else:
		ref.valid_rawvotes = Rawvote.objects.filter(ref = ref).filter(json__isnull=False).exclude(email="test@exemple.fr")
		ref.sent_rawvotes = Rawvote.objects.filter(ref=ref).exclude(status="INIT").exclude(email="test@exemple.fr")

	context = {"ref":ref}
	return render(request, template, context)


#Ce qu'on envoie pour lancer le dépouillement
def ref_depouillement(request, hash):
	if request.method=="POST":
		ref = Ref.objects.get(hash=hash)
		if ref.depouillement == "ALT":
			trait_alter(ref)
		if ref.depouillement == "CLASSIC":
			if ref.crypted:
				trait_classic(ref, request.FILES["private_key"])
			else:
				trait_classic(ref)
		
		ref.status="FINISHED"
		ref.save()
	return HttpResponseRedirect(reverse('voteadmin_depouillement', args = (hash,)))

#Fonction qui calcul les résultats pour un vote classic
def trait_classic(ref, private_key=None):
	
	if ref.crypted:
		valid_rawvotes = Rawvote.objects.filter(ref = ref).exclude(crypted_json__isnull=True).exclude(email="test@exemple.fr")
	else:
		valid_rawvotes = Rawvote.objects.filter(ref = ref).exclude(json__isnull=True).exclude(email="test@exemple.fr")
	
	Tour.objects.filter(ref=ref).delete()
	tour = Tour()
	tour.ref = ref
	results = {}

	#Initialisation du dictionnaire
	questions = Question.objects.filter(ref = ref)
	for question in questions:
		options = Option.objects.filter(question = question)
		for option in options:
			results[option.id] = 0
	
	#Remplissage du dictionnaire
	if ref.crypted:
		cipher = PKCS1_OAEP.new(RSA.importKey(private_key.read()))

	for valid_rawvote in valid_rawvotes:
		if ref.crypted:	
			string_json = cipher.decrypt(valid_rawvote.crypted_json).decode("utf-8")
			decrypted_json = eval(string_json)
			for ques_id,opt_id in decrypted_json.items():
				results[int(opt_id)] = results[int(opt_id)] + 1		
		else:
			for ques_id,opt_id in valid_rawvote.json.items():
				results[int(opt_id)] = results[int(opt_id)] + 1
	
	tour.results= results
	tour.save()

#Fonction qui calcul les résultats pour un jugement majoritaire
def trait_jug(ref):
	questions = Question.objects.filter(ref = ref)
	valid_rawvotes = Rawvote.objects.filter(ref = ref).exclude(json__isnull=True).exclude(email="test@exemple.fr")
	Tour.objects.filter(ref=ref).delete()

	tour = Tour()
	tour.ref = ref
	results = {}

	for question in questions:
		question.options = Option.objects.filter(question = question)
		for option in question.options:
			results[option.id] = {}
			for keyjug, jugoption in ref.jugoptions.items():
				results[option.id][int(keyjug)] = 0
	
	for valid_rawvote in valid_rawvotes:
		for opt_id,jug_opt in valid_rawvote.json.items():
			results[int(opt_id)][int(jug_opt)] = results[int(opt_id)][int(jug_opt)] + 1
	
	tour.results= results
	tour.save()

#Fonction qui calcul les résultats pour un vote alternatif
def trait_alter(ref):
	questions = Question.objects.filter(ref = ref)
	valid_rawvotes = Rawvote.objects.filter(ref = ref).exclude(json__isnull=True).exclude(email="test@exemple.fr")
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
	Rawvote.objects.filter(ref=ref).exclude(email="test@exemple.fr").delete()

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

def fakevotes_classic(id_ref):
	import random
	import string
	letters = string.ascii_lowercase

	ref = Ref.objects.get(id=id_ref)
	# questions = Question.objects.get(ref=ref)
	# for question in questions:
	# 	question.option = 

	Rawvote.objects.filter(ref=ref).exclude(email="test@exemple.fr").delete()

	for i in range(100):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"6": "10", "7": "12"}
		rawvote.save()

	for i in range(90):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"6": "11", "7": "13"}
		rawvote.save()

	for i in range(80):
		rawvote = Rawvote()
		rawvote.ref = ref
		rawvote.email = ''.join(random.choice(letters) for i in range(10))+"@gmail.com"
		rawvote.code = ''.join(random.choice(letters) for i in range(50))
		rawvote.json = {"6": "10", "7": "13"}
		rawvote.save()

#Afficher les résultats des votes alternatifs
def ref_results(request, id_ref):
	ref = Ref.objects.get(id = id_ref)
	
	if ref.depouillement=="ALT":
		template = "newref/voteresults_alt.html" 
		ref.questions = Question.objects.filter(ref = ref)
		for question in ref.questions:
			question.touralters = Touralter.objects.filter(question=question)
			question.options = Option.objects.filter(question = question)	
			
			for option in question.options:
				option.horizontal_results = {}
				for touralter in question.touralters:
					option.horizontal_results[touralter.num] = touralter.results[str(option.id)]

	elif ref.depouillement=="CLASSIC":
		template = "newref/voteresults_classic.html"
		tour = Tour.objects.get(ref=ref)
		
		ref.questions = Question.objects.filter(ref = ref)
		for question in ref.questions:
			question.options = Option.objects.filter(question = question)	
			for option in question.options:
				option.results = tour.results[str(option.id)]

	elif ref.depouillement=="JUG":
		template = "newref/voteresults_jug.html"
		tour = Tour.objects.get(ref=ref)
		
		#Organisation des données par option
		ref.questions = Question.objects.filter(ref = ref)
		for question in ref.questions:
			question.options = Option.objects.filter(question = question)	
			for option in question.options:
				option.results = tour.results[str(option.id)]
	
		#Organisation des données par jugoption
		ref.datas = {}
		for keyjug, jugopt in ref.jugoptions.items():
			data = []
			for key,value in tour.results.items():
				data.append(value[keyjug])
			ref.datas[keyjug] = data
			print(data)


	context = {"ref": ref}
	return render(request, template, context)

def communicate_results(request, hash):
	a=1
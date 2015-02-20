from django.shortcuts import render, render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from myapp.models import *
from myapp.forms import *

# Create your views here.

@login_required
def test_view(request, *args, **kwargs):
	return HttpResponse('HEY THERE BEAUTIFUL!')

def login_view(request, *args, **kwargs):
	if request.method == 'GET':
		return render(request, 'login.html')
	else:
		user = authenticate(username=request.POST['username'], password=request.POST['password'])

		if user is not None:
			# the password verified for the user
			if user.is_active:
				return HttpResponse("User is valid, active and authenticated")
			else:
				return HttpResponse("The password is valid, but the account has been disabled!")
		else:
			# the authentication system was unable to verify the username and password
			return HttpResponse("The username and password were incorrect.")


def add_to_existing(wizard):
	# try to get the cleaned data of step 1
	cleaned_data = wizard.get_cleaned_data_for_step('contact_info') or {'add_to_existing': False}
	# check if the field ``leave_message`` was checked.
	return cleaned_data.get('add_to_existing')


def not_add_to_existing(wizard):
	return not add_to_existing(wizard)

FORMS = [("contact_info", ContactForm1),
		 ("existing_list", ContactForm2),
		 ("new_list", ContactForm3)]

TEMPLATES = {
	"contact_info": "contact_info.html",
	"existing_list": "existing_list.html",
	"new_list": "new_list.html"}

class ContactWizard(SessionWizardView):
	condition_dict = {
		'contact_info': True,
		'existing_list': add_to_existing,
		'new_list': not_add_to_existing
	}

	def get_template_names(self):
		return [TEMPLATES[self.steps.current]]

	def done(self, form_list, form_dict, **kwargs):
		ci = form_dict['contact_info'].cleaned_data
		name = ci['name']
		number = ci['number']
		age = ci['age']

		new_contact = Contact(name=name, number=number, age=age)

		dest_contact_list = None

		if 'existing_list' in form_dict:
			el = form_dict['existing_list'].cleaned_data
			dest_contact_list = el['contact_list']
		elif 'new_list' in form_dict:
			nl = form_dict['new_list'].cleaned_data
			name = nl['name']
			private = nl['private']

			dest_contact_list = ContactList.objects.create(name=name, private=private)

		new_contact.contact_list = dest_contact_list
		new_contact.save()

		return render_to_response('done.html', {
			'new_contact_id' : new_contact.id,
			'contact_lists' : ContactList.objects.all(),
		})



### IGNORE THIS VIEW ###

def car_view(request, *args, **kwargs):
	if request.method == 'GET':
		form = CarForm()
		return render(request, 'car.html', {'form': form})
	else:
		return HttpResponse('Use GET pls...')
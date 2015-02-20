from django import forms

from myapp.models import *

class ContactForm1(forms.Form):
	name = forms.CharField()
	number = forms.CharField()
	age = forms.IntegerField()
	add_to_existing = forms.BooleanField(required=False, label="Add to existing contact list")

class ContactForm2(forms.Form):
	contact_list = forms.ModelChoiceField(queryset=ContactList.objects.all())

class ContactForm3(forms.Form):
	name = forms.CharField()
	private = forms.BooleanField(required=False)
# class ContactForm2(forms.Form):
# 	message = forms.CharField(widget=forms.Textarea)




### IGNORE THIS FORM ###

class CarForm(forms.Form):
	make = forms.CharField()
	model = forms.CharField()

	def __init__(self, *args, **kwargs):
		super(CarForm, self).__init__(*args, **kwargs)
		self.fields['year'] = forms.ChoiceField(choices=[(y.id, y.name) for y in Year.objects.all()])
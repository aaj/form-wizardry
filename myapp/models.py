from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ContactList(models.Model):
	name = models.CharField(max_length=30)
	private = models.BooleanField(default=True)

	def __unicode__(self):
		res = self.name
		res += ' (private)' if self.private else ''
		return res


class Contact(models.Model):
	contact_list = models.ForeignKey(ContactList)
	name = models.CharField(max_length=50)
	number = models.CharField(max_length=15)
	age = models.IntegerField()

	def __unicode__(self):
		return '%s (age: %d)' % (self.name, self.age)

### THESE MODELS ARE FOR SOMETHING ELSE I WAS TESTING. THESE HAVE NOTHING TO DO WITH THE FORM WIZARD! ###

class Year(models.Model):
	name = models.CharField(max_length=4)

class Car(models.Model):
	make = models.CharField(max_length=20)
	model = models.CharField(max_length=20)
	year = models.CharField(max_length=10)
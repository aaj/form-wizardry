# form-wizardry

So, this was my little experiment with Django Form Wizard. I'll try to go over the basics of what I did.

# Models

First, I made a couple of sample models.

```python
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
	number = models.CharField(max_length=15) #phone number
	age = models.IntegerField()

	def __unicode__(self):
		return '%s (age: %d)' % (self.name, self.age)
```

Pretty simple stuff. A ```ContactList``` model, which has a name, and a boolean field called ```private```.
The ```private``` field doesn't really do anything. I just wanted to have a couple of fields in the model.
Next is the ```Contact``` model, which also has some filler fields, but also a ```ForeignKey``` field to
```ContactList```. The idea is to have a bunch of contact lists, each with a separate name, and each with it's
own set of contacts.

So, for instance, we could have a contact list named "Actors" and have "Brad Pitt" and "Jennifer Lawrence" in there,
and another contact list named "Musicians" with "Kanye West" and "Beck".

# Forms

For my form wizard, I wanted the user to first input the contact details (name, number, and age). So I made a Form
class for this first step, called ```ContactForm1```:

```python
class ContactForm1(forms.Form):
	name = forms.CharField()
	number = forms.CharField()
	age = forms.IntegerField()
```

After this first step, I want my wizard to be able to branch into two directions: Assign the newly
created contact to a **new contact list**, or to an **existing contact list**. To do that, we have to 
ask the user which one of those two options he wants to do, and we have to ask him in the first step. So I
added another field to my ```ContactForm1```:

```python
class ContactForm1(forms.Form):
	name = forms.CharField()
	number = forms.CharField()
	age = forms.IntegerField()
	
	# this will show up as a checkbox that the user can tick if he wants to add the new contact
	# to an existing contact list, or leave blank if he wants to create a new contact list.
	add_to_existing = forms.BooleanField(required=False, label="Add to existing contact list")
```

Then I made form classes for each of these two possible cases:

```python
class ContactForm2(forms.Form):
	contact_list = forms.ModelChoiceField(queryset=ContactList.objects.all())
  # forms.ModelChoiceField will be rendered as a standard html <select> drop down, with the options
  # coming from ContactList.objects.all(). So, all existing contact lists will be available as options.
  
class ContactForm3(forms.Form):
	name = forms.CharField()
	private = forms.BooleanField(required=False)
```

As you can guess, ```ContactForm2``` is used when the user ticks the ```add_to_existing``` checkbox, and ```ContactForm3```
is used otherwise. We'll get to how this branching is determined in a bit.

# Form Wizard

To create a Form Wizard, you have to do a few things. First, you have to define a list of ```Form``` classes which will
represent each of your Wizard's steps. I had 3 steps so:

```python
FORMS = [("contact_info", ContactForm1), # input contact name, number and age, and the add_to_existing checkbox
		 ("existing_list", ContactForm2), # select an existing contact list form a drop down menu
		 ("new_list", ContactForm3)] # input new contact list name and whether or not it is private
```

The strings are just human-readable names that you can assign to each step of your wizard. If you don't assign any names,
you can still find them through a zero-based index. I prefer naming them.

Next up, you have to define a ```dict``` with the templates that each of your steps uses:

```python
TEMPLATES = {
	"contact_info": "contact_info.html",
	"existing_list": "existing_list.html",
	"new_list": "new_list.html"
}
```

Here we map each of the steps' names to a template file. These templates must live inside of your ```TEMPLATE_DIRS``` 
setting. You are responsible for making these templates yourself, but Django gives you a guarantee: each one of your
templates will be given a ```wizard``` variable to work with. Great. But...what the hell is that and how can we use it?

The Django docs explain what that wizard variable is and what it contains: https://docs.djangoproject.com/en/1.7/ref/contrib/formtools/form-wizard/#creating-templates-for-the-forms

Basically, it's a collection of a bunch of stuff that your template could use to render itself property. Here is the template
for the first step of my wizard, ```contact_info.html```:

```html
<!DOCTYPE html>
<html>
	<head>
		<title></title>
	</head>

	<body>
		<h1>Step {{ wizard.steps.step1 }} of {{ wizard.steps.count }}</h1>
		<h3>Add new contact</h3>
		<p>Fill out your contact details</p>

		<form action="" method="POST">
			{% csrf_token %}
			{{ wizard.management_form }}
			{{ wizard.form.as_p }}
			<input type="submit" value="Next"/>
		</form>
	</body>
</html>
```

Ok, so let's go over this:

1. ```<h1>Step {{ wizard.steps.step1 }} of {{ wizard.steps.count }}</h1>```: Here we can see the ```wizard``` variable at work.
We can get the current step that our wizard is in with ```wizard.steps.step1```. We can get the total number of steps in our
wizard with ```wizard.steps.count```. I am using those values to show a helpful "Step X Of Y" at the top of our form. Since this
template is for our first step, and since there are only 3 steps, it should always read "Step 1 Of 3" (or at least, that's what
I was expecting. More on this later).

2. ```<form action="" method="POST">```: Django Form Wizards expect your forms to use the POST method. They also expect you to always submit
your forms to one url (hence the ```action=""```). I believe you can customize each step with it's own url, but that's not our concern at the moment.

3. ```{% csrf_token %}```: Csrf protection for our forms. This isn't FormWizard specific: this should go inside **any and every** form that
uses the POST method.

4. ```{{ wizard.management_form }}```: Here's where it gets interesting. Here we use the wizard varibale again, but this time
to print out a management_form. What's a management form? Well, our FormWizard needs to keep track of stuff as we move from step
to step. The way it does this is by storing some stuff in hidden inputs on our html form. And those hidden inputs get placed
there with this line. So, this is **mandatory** for all steps of every FormWizard.

5. ```{{ wizard.form.as_p }}```: Here is where our form gets rendered. Remember, we mapped each of this FormWizard's steps
to a form:```FORMS = [("contact_info", ContactForm1), ("existing_list", ContactForm2), ("new_list", ContactForm3)]```.
So an instance of that form class will also be made available to our template, in the variable ```wizard.form```. On this line,
we're using that form and calling it's ```as_p``` function, which will render whatever widgets are needed. 

6. ```<input type="submit" value="Next"/>```: We gotta add the submit button ourselves, because django forms don't do this for us.

Great. Hopefully you got that. The templates for my steps 2 and 3 are pretty much the same. All that changes is the header.

Our FormWizard isn't ready yet, but lets see how this form would look once rendered:

![alt text](http://i.imgur.com/oeU1H7d.png "Step 1")

Beautiful...except that it says "Step 1 of 2". Didn't we have 3 Steps? Yeah, we'll get to that in a moment. Read on.

Once I finished all three template files, I created my WizardView class:

```python
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
```

**WHOA WHOA WHOA, what is all this crap?** Well, this is my FormWizard, all finished up. Lets take it step by step:

* First, I declared my class named ```ContactWizard```, which inherits from ```SessionWizard```. So you're gonna need an import:
```python
from django.contrib.formtools.wizard.views import SessionWizardView

class ContactWizard(SessionWizardView):
  pass
```

* Next, I declared the ```done``` function. It's covered in the docs. This function gets called when your users finish the
final step of your wizard:
```python
from django.contrib.formtools.wizard.views import SessionWizardView

class ContactWizard(SessionWizardView):
  def done(self, form_list, form_dict, **kwargs):
    pass
```
It takes a ```form_list``` and a ```form_dict``` argument. These contain form objects, which in turn contain all the data
that your user submitted. At this point, when this function gets called, it is safe to assume that all the data is valid,
so you can use all the data from any of the steps as you please.

* We also need a way for our ContactWizard to know which templates it's going to use. So we declare ```get_template_names``` function:
```python
from django.contrib.formtools.wizard.views import SessionWizardView

class ContactWizard(SessionWizardView):
  def get_template_names(self):
  		return [TEMPLATES[self.steps.current]]
  	
  def done(self, form_list, form_dict, **kwargs):
    pass
```
What this function does is return a template name depending on our wizard's current step. Notice it is using the ```TEMPLATES```
dict that we defined earlier.

* Now, remember how we wanted our wizard to branch depending on a checkbox in the first step? Well, turns out that we can also
do that with django form wizards. One way to do it is to define a dictionary named ```condition_dict``` inside of our 
ContactWizard class:
```python
from django.contrib.formtools.wizard.views import SessionWizardView

class ContactWizard(SessionWizardView):
  condition_dict = {
		'contact_info': True,
		'existing_list': add_to_existing,
		'new_list': not_add_to_existing
	}
	
  def get_template_names(self):
  		return [TEMPLATES[self.steps.current]]
  	
  def done(self, form_list, form_dict, **kwargs):
    pass
```
The ```condition_dict``` should map step names to ```True``` or ```False```, or to any function that will return ```True```
or ```False```. What this dict is telling us is that:

1. The 'contact_info' step should **always** be shown (hence the ```True```)
2. The 'existing_list' step will depend on the result of a function named ```add_to_existing```
3. The 'new_list' step will depend on the result of a function named ```not_add_to_existing```

Ok great. So where are those functions? You have to provide them:

```python
def add_to_existing(wizard):
	# try to get the cleaned data of step 1
	cleaned_data = wizard.get_cleaned_data_for_step('contact_info') or {'add_to_existing': False}
	return cleaned_data.get('add_to_existing')


def not_add_to_existing(wizard):
	return not add_to_existing(wizard)
```

I defined these two functions **outside** of my ContactWizard class. Notice that they take a ```wizard``` object. Django
passes it to them when it needs to determine wheter or not to show a step. The ```add_to_existing``` function is checking
if the add_to_existing checkbox was ticked in the first step, and returning ```True``` if it was, else ```False```. The
```not_add_to_existing``` function is returning the opposite of that. **Disclaimer:** I don't know if this is really the
best way, but I needed the wizard to show either step 2 or step 3, but never both. This is the best I could come up with.

And here is where I'm stumped: Remember our html form saying "Step 1 of 2" even though we technically have 3 steps? I believe
django is working some magic here to "know" that only two of my steps will be used at any given time. It's weird, I know. I
mean, I haven't even gotten past the first step, I haven't even filled out the form, and yet it knows that it will show me
two steps only. I'm sure there's a logical explanation for it, but if you know, please don't tell me what it is.
I'd rather believe that Django is sentient and can read/understand my source code <3.

* Moving on: We've got our ContactWizard hooked up to it's templates, and our conditioning setup to determine the flow of our
steps. Now we get to the meat of our ContactWiazrd: Deciding what to do when the user submits the last form of our wizard. We
can do that inside of our ```done``` function:
```python
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
```

Let's dig in:

```python
ci = form_dict['contact_info'].cleaned_data
name = ci['name']
number = ci['number']
age = ci['age']

new_contact = Contact(name=name, number=number, age=age)
````
Here i'm extracting the ```cleaned_data``` from our 'contact_info' form (the first step of our wizard), and storing it in a 
variable named ``ci``. Remember: when this function get's called, all of our forms have already been filled out by the user 
and validated. You can use their data however you like. I'm extracting all of the fields name, number and age into 
variables of their own. Then, I'm using them to create a new Contact object. I haven't saved it yet, because each
contact needs a ForeignKey to a ContactList, and we do not yet know if the user selected a pre-existing one, or chose
to create a new one on the spot.

Next up:

```python
dest_contact_list = None

if 'existing_list' in form_dict:
	el = form_dict['existing_list'].cleaned_data
	dest_contact_list = el['contact_list']
elif 'new_list' in form_dict:
	nl = form_dict['new_list'].cleaned_data
	name = nl['name']
	private = nl['private']

	dest_contact_list = ContactList.objects.create(name=name, private=private)
```

We define ```dest_contact_list``` as None. This variable will store the **dest**ination contact list for the new Contact
we just created. We do that by first checking ```if 'existing_list' in form_dict```. ```existing_list``` was the name
of our second step. With this, we are checking to see if a form was submitted for this step or not. If it was, we simply
pluck the contact list from the form's cleaned data and put it in ```dest_contact_list```. If a form **wasn't** submitted 
for this step, that means the user passed to step 3, in which he typed in the name for a **new** contact list. In that case,
we pluck the ```name``` and ```private``` data from the ```new_list``` form, and use it to **create a new ContactList object***,
save it into the database, and store the newly created object in ```dest_contact_list```.

The point of this is that, no matter if the user went with step 2 (used existin contact list) or step 3 (created a new one), the
```dest_contact_list``` variable will store a reference to a contact list, which we need in order to save the new contact. Which
is what we do next:

```python
new_contact.contact_list = dest_contact_list
new_contact.save()

return render_to_response('done.html', {
	'new_contact_id' : new_contact.id,
	'contact_lists' : ContactList.objects.all(),
})
```

Here we assigne ```dest_contact_list``` to the ```contact_list``` property  of our ```new_contact```, and then save it. At
this point, our new contact has been saved to the database. What is left now is to render a "done" page. Mine looks like this:

```html
<!DOCTYPE html>
	<html>
	<head>
		<title></title>
	</head>
	<body>
		<h2>New contact saved successfully!<h2>

		<h3>Contact Lists</h3>
		<ul>
			{% for cl in contact_lists %}
				<li>{{ cl }}
					<ul>
						{% for c in cl.contact_set.all %}
							{% if c.id == new_contact_id %}
								<li style="color:red;">(new) {{ c }}</li>
							{% else %}
								<li>{{ c }}</li>
							{% endif %}
						{% endfor %}
					</ul>
				</li>
			{% endfor %}
		</ul>
	</body>
</html>
```

Basically it just shows you all the contact lists that you've created, and all the contacts inside of each one.

One last thing you have to do, is to hook up your FormWizard to a url. Here's my urls.py:

```python
from django.conf.urls import patterns, include, url
from django.contrib import admin
from myapp.views import *
from myapp.forms import *

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^contacts/', ContactWizard.as_view(FORMS), name='contacts'),
)
```

That should be it, I think. Let's give it a try:

![alt text](http://i.imgur.com/oeU1H7d.png "Step 1")

Step one looks good...

![alt text](http://i.imgur.com/f9qmRI3.png "Step 1")

Nice...validation seems to be working fine...

![alt text](http://i.imgur.com/0rfiCjo.png "Step 1")

We fill out all the fields, and leave the "Add to existing" checkbox unticked...

![alt text](http://i.imgur.com/RkHgI19.png "Step 3")

Good. Since we didn't tick the checkbox, it shows us this form, to create a new ContactList. We fill out the details and...

![alt text](http://i.imgur.com/FM94Yxj.png "Done")

Great. Our contact was saved into a newly created "Actors" list. Let's try one more:

![alt text](http://i.imgur.com/aWRxVI5.png "Step 1")

Step one again. This time we **do** want to use an existing list, so we tick the checkbox. When we submit this form...

![alt text](http://i.imgur.com/eJQp4Go.png "Step 2")

It brings us to this other form. Notice that it says "Step 2 of 2". We select one of the available contact lists and
submit this form...

![alt text](http://i.imgur.com/7BfnwQk.png "Done")

And there we go. Another contact saved, this time to an existing form.

# Conclusion

I know that this is a lot to wrap your mind around if you're new to Django, and I probably didn't do a great job of explaining
it, but hopefully I showed you enough that you can get your own Form Wizard going...or at least left you with enough questions
to find your way.

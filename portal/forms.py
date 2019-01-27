from django import forms
from .models import Subscription, Address, Payment, Label, SubscriptionLabel
from django.utils.translation import ugettext_lazy as _

class SubscriptionForm(forms.ModelForm):
	"""Create new subscription."""

	class Meta:
		model = Subscription
		exclude = ('active',)

class PaymentForm(forms.ModelForm):

	class Meta:
		model = Payment
		fields = ('method','refId','amount','details',)

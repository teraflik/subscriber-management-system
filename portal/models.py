import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class Subscription(models.Model):
	SUB_HALFYEAR = 6
	SUB_YEAR = 12
	SUB_TWOYEAR = 24
	SUB_FIVEYEAR = 60
	SUB_TENYEAR = 120
	SUB_TWENTYYEAR = 240
	SUB_LIFETIME = 0

	PERIOD_CHOICES = (
		(SUB_TWOYEAR, _("Two Years")),
		(SUB_FIVEYEAR, _("Five Months")),
		(SUB_TENYEAR, _("Ten Years")),
		(SUB_TWENTYYEAR, _("Twenty Years")),
		(SUB_LIFETIME, _("Lifetime"))
	)
	
	createdDate = models.DateField(default=timezone.now, verbose_name=_("Start Date"))
	renewDate = models.DateField(default=timezone.now, verbose_name=_("Last Renew Date"))
	period = models.PositiveIntegerField(choices=PERIOD_CHOICES, default=12, verbose_name=_("Period"))
	expireDate = models.DateField(null=True, blank=True, verbose_name=_("Expiration Date"))
	agent = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Agent"))
	#payment = models.OneToOneField('Payment', null=True, blank=True, on_delete=models.SET_NULL)
	#address = models.OneToOneField('Address', null=True, blank=True, on_delete=models.SET_NULL)
	active = models.BooleanField(default=True, verbose_name="Is Subscription Active?")

	def __str__(self):
		return self.address.fullName

	def calcExpireDate(self):
		if self.period == 0:
			return None
		expireDate = self.renewDate + relativedelta(months=self.period)
		return expireDate

	def isExpired(self):
		if self.period == 0:
			return False
		return self.calcExpireDate() < datetime.date.today()

class Address(models.Model):
	subscription = models.OneToOneField('Subscription', related_name="address", on_delete=models.CASCADE)
	fullName = models.CharField(max_length=100, verbose_name=_("Full Name"))
	street = models.TextField(verbose_name=_("Street Address"))
	city = models.CharField(max_length=30, verbose_name=_("City"))
	province = models.CharField(max_length=30, blank=True, verbose_name=_("State"))
	code = models.CharField(max_length=10, verbose_name=_("Pincode"))
	contact1 = models.CharField(max_length=15, blank=True, verbose_name=_("Contact Number 1"))
	contact2 = models.CharField(max_length=15, blank=True, verbose_name=_("Contact Number 2 (Optional)"))

	class Meta:
		verbose_name_plural = "Addresses"
	
	def getLabel(self):
		label = self.fullName + "<br /><br />"
		label = label + self.street + "<br />" + self.city + "<br /> " + self.province + " - " + self.code + "<br />"
		label = label + "Contact: " + self.contact1
		return label
	
	@property
	def getContact(self):
		return self.contact1 or self.contact2 or None

	def __str__(self):
		return self.fullName

class Payment(models.Model):
	PAY_CASH = "Cash"
	PAY_CHEQUE = "Cheque"
	PAY_DD = "Demand Draft"
	PAY_NETB = "Net Banking"
	PAY_PAYTM = "PayTM"
	PAY_UPI = "UPI"
	PAY_FREE = "Free"

	METHOD_CHOICES = [
		(PAY_CASH, _("Cash")),
		(PAY_PAYTM, _("PayTM")),
		(PAY_UPI, _("UPI")),
		(PAY_NETB, _("Net Banking")),
		(PAY_CHEQUE, _("Cheque")),
		(PAY_DD, _("Demand Draft")),
		(PAY_FREE, _("Free")),
	]

	subscription = models.OneToOneField('Subscription', related_name="payment", on_delete=models.CASCADE)
	method = models.CharField(max_length=20, blank=True, choices=METHOD_CHOICES, verbose_name=_("Payment Method"))
	refId = models.CharField(max_length=80, blank=True, verbose_name=_("Reference ID"))
	amount = models.DecimalField(max_digits=11, blank=True, null=True, decimal_places=2, verbose_name=("Payment Amount"))
	details = models.TextField(blank=True, verbose_name=_("Details"))

	def __str__(self):
		return self.method

class Label(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name

class SubscriptionLabel(models.Model):
	subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)
	label = models.ForeignKey('Label', on_delete=models.CASCADE)

	class Meta:
		unique_together = [("subscription", "label")]

	def __str__(self):
		return self.subscription.address.fullName + " in " + self.label.name

		
@receiver(pre_save, sender=Subscription)
def generateExpireDate(sender, instance, **kwargs):
	if instance.period == 0:
		instance.expireDate = datetime.date.max
	else:
		instance.expireDate = instance.calcExpireDate()
	instance.active = not instance.isExpired()
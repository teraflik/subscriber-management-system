import datetime
import pprint
from dateutil.relativedelta import relativedelta
from rangefilter.filter import DateRangeFilter
from reportlab.lib.pagesizes import inch, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from portal.models import Subscription, Address, Payment, Label, SubscriptionLabel

admin.site.site_header = "Hare Krishna Prakash"
admin.site.site_title = "Hare Krishna Parivaar"
admin.site.index_title = "Welcome to Hare Krishna Parivaar"

class ExpiringSoonFilter(admin.SimpleListFilter):
	title = _("Expiring Soon")
	parameter_name = 'expiringSoon'

	def lookups(self, request, model_admin):
		return (
			(0, 'Expired'),
			(1, 'Expiring in 1 Month'),
			(6, 'Expiring in 6 Months'),
			(12, 'Expiring in 12 Months'),
		)

	def queryset(self, request, queryset):
		today = datetime.date.today()
		if self.value() is not None:
			value = int(self.value())
			if value == 0:
				return queryset.filter(expireDate__lte=today)
			elif value >= 0:
				return queryset.filter(expireDate__gte=today, expireDate__lte=today+relativedelta(months=value))
		return queryset
		
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ('fullName', 'street', 'city', 'province', 'code',)
	list_filter = ('city','province')
	search_fields = ['fullName', 'street', 'city', 'province', 'code', 'contact1']

admin.site.register(Label)
#admin.site.register(SubscriptionLabel)

class AddressInline(admin.StackedInline):
	model = Address

class PaymentInline(admin.TabularInline):
	model = Payment

class SubscriptionLabelInline(admin.StackedInline):
	model = SubscriptionLabel

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
	actions_on_bottom = True
	actions_on_top = False
	readonly_fields = ['expireDate', 'active']

	list_display = ('__str__', 'contact', 'createdDate', 'renewDate', 'payment', 'period', 'expireDate', 'active',)
	#list_editable = ('renewDate', 'period',)

	list_filter = (
		ExpiringSoonFilter,
		('expireDate', DateRangeFilter),
		'renewDate',
		'active',
	)
	actions = ['printLabels']
	inlines = [AddressInline, PaymentInline, SubscriptionLabelInline]

	def contact(self, obj):
		return obj.address.getContact

	def printLabels(self, request, queryset):
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'filename="labels_for_print.pdf"'
		cm = 2.54
		doc = SimpleDocTemplate(response, showBoundary=1, title="Labels")
		elements = []
		styles = getSampleStyleSheet()

		width, height = A4

		data = []
		i = 0
		row = []
		for obj in queryset:
			address = obj.address.getLabel()
			if(i%2 == 0 and i>0):
				data.append(row)
				row = []
			row.append(address)
			i = i+1
		data.append(row)
		#pprint.pprint(data)
		t=Table(data)

		elements.append(t)
		doc.build(elements)
		
		return response

	contact.short_description = "Contact"
	printLabels.short_description = "Print selected labels"
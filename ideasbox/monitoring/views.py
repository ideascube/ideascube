from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  TemplateView, UpdateView, View)

from ideasbox.views import CSVExportMixin

from .forms import (EntryForm, ExportEntryForm, ExportLoanForm,
                    InventorySpecimenForm, LoanForm, ReturnForm, SpecimenForm)
from .models import (Entry, Inventory, InventorySpecimen, Loan, Specimen,
                     StockItem)

user_model = get_user_model()


class EntryView(FormView):
    fields = '__all__'
    template_name = 'monitoring/entry.html'
    form_class = EntryForm
    success_url = reverse_lazy('monitoring:entry')

    def form_valid(self, form):
        count = 0
        module = form.cleaned_data['module']
        activity = form.cleaned_data['activity']
        partner = form.cleaned_data['partner']
        activity_select = form.cleaned_data['activity_list']
        if not activity and activity_select:
            activity = activity_select
        for serial in form.cleaned_data['serials']:
            try:
                user = user_model.objects.get(serial=serial)
            except user_model.DoesNotExist:
                msg = _('No user found with serial {serial}')
                msg = msg.format(serial=serial)
                messages.add_message(self.request, messages.ERROR, msg)
            else:
                Entry.objects.create(user=user, module=module,
                                     activity=activity, partner=partner)
                count += 1
        if count:
            msg = _('Created {count} entries')
            msg = msg.format(count=count)
            messages.add_message(self.request, messages.SUCCESS, msg)
        else:
            msg = _('No entry created.')
            messages.add_message(self.request, messages.WARNING, msg)
        return super(EntryView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EntryView, self).get_context_data(**kwargs)
        context['entries'] = Entry.objects.all()[:50]
        context['export_form'] = ExportEntryForm()
        context['MONITORING_ENTRY_EXPORT_FIELDS'] = settings.MONITORING_ENTRY_EXPORT_FIELDS  # noqa
        return context

entry = staff_member_required(EntryView.as_view())


class ExportEntry(CSVExportMixin, View):
    prefix = 'entry'

    def get(self, *args, **kwargs):
        self.form = ExportEntryForm(self.request.GET)
        if self.form.is_valid():
            return self.render_to_csv()
        else:
            msg = _('Error while processing entries export')
            messages.add_message(self.request, messages.ERROR, msg)
            messages.add_message()
            return HttpResponseRedirect(reverse_lazy('monitoring:entry'))

    def get_headers(self):
        self.fields = ['module', 'date', 'activity', 'partner']
        self.fields.extend(settings.MONITORING_ENTRY_EXPORT_FIELDS)
        return self.fields

    def get_items(self):
        qs = Entry.objects.order_by('created_at')
        if self.form.cleaned_data['since']:
            qs = qs.filter(created_at__gte=self.form.cleaned_data['since'])
        return qs

    def get_row(self, entry):
        row = {'module': entry.module, 'date': entry.created_at,
               'activity': entry.activity, 'partner': entry.partner}
        for field in settings.MONITORING_ENTRY_EXPORT_FIELDS:
            row[field] = getattr(entry.user, field, None)
        return row

export_entry = staff_member_required(ExportEntry.as_view())


class StockListMixin(object):

    def get_stock(self):
        stock = []
        for key, name in StockItem.MODULES:
            stock.append({
                'key': key,
                'name': name,
                'objects': StockItem.objects.filter(module=key)
            })
        return stock


class Stock(StockListMixin, TemplateView):
    template_name = "monitoring/stock.html"
    model = StockItem

    def get_context_data(self, **kwargs):
        return {
            'stock': self.get_stock(),
            'inventory_list': Inventory.objects.all()
        }
stock = staff_member_required(Stock.as_view())


class InventoryDetail(StockListMixin, DetailView):
    model = Inventory
    template_name = 'monitoring/inventory.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryDetail, self).get_context_data(**kwargs)
        context['stock'] = self.get_stock()
        context['inventoryspecimen_form'] = InventorySpecimenForm(
            initial={'inventory': self.object})
        return context

inventory = staff_member_required(InventoryDetail.as_view())


class InventoryUpdate(UpdateView):
    model = Inventory
    fields = '__all__'
inventory_update = staff_member_required(InventoryUpdate.as_view())


class InventoryCreate(CreateView):
    model = Inventory
    fields = '__all__'
inventory_create = staff_member_required(InventoryCreate.as_view())


class InventoryDelete(DeleteView):
    model = Inventory
    success_url = reverse_lazy('monitoring:stock')
inventory_delete = staff_member_required(InventoryDelete.as_view())


class InventoryExport(CSVExportMixin, DetailView):
    model = Inventory

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_csv()

    def get_headers(self):
        self.headers = ['module', 'name', 'description', 'barcode', 'serial',
                        'count', 'comments', 'status']
        return self.headers

    def get_items(self):
        return Specimen.objects.all()

    def get_row(self, specimen):
        return {
            'module': specimen.item.module,
            'name': specimen.item.name.encode('utf-8'),
            'description': specimen.item.description.encode('utf-8'),
            'barcode': specimen.barcode,
            'serial': specimen.serial,
            'count': specimen.count,
            'comments': specimen.comments.encode('utf-8'),
            'status': specimen.count if specimen in self.object else 'ko'
        }

    def get_filename(self):
        filename = "_".join([
            'inventory',
            settings.IDEASBOX_ID,
            str(self.object.made_at)
        ])
        return filename
inventory_export = staff_member_required(InventoryExport.as_view())


class StockItemUpdate(UpdateView):
    model = StockItem
    fields = '__all__'
stockitem_update = staff_member_required(StockItemUpdate.as_view())


class StockItemCreate(CreateView):
    model = StockItem
    fields = '__all__'
stockitem_create = staff_member_required(StockItemCreate.as_view())


class StockItemDelete(DeleteView):
    model = StockItem
    success_url = reverse_lazy('monitoring:stock')
stockitem_delete = staff_member_required(StockItemDelete.as_view())


class SpecimenUpdate(UpdateView):
    model = Specimen
    form_class = SpecimenForm
specimen_update = staff_member_required(SpecimenUpdate.as_view())


class SpecimenCreate(CreateView):
    model = Specimen
    form_class = SpecimenForm

    def get_initial(self):
        item = get_object_or_404(StockItem, pk=self.kwargs['item_pk'])
        return {'item': item}
specimen_create = staff_member_required(SpecimenCreate.as_view())


class SpecimenDelete(DeleteView):
    model = Specimen
    success_url = reverse_lazy('monitoring:stock')
specimen_delete = staff_member_required(SpecimenDelete.as_view())


class InventorySpecimenAdd(View):

    def get(self, request, *args, **kwargs):
        inventory = get_object_or_404(Inventory,
                                      pk=self.kwargs['inventory_pk'])
        specimen = get_object_or_404(Specimen, pk=self.kwargs['specimen_pk'])
        InventorySpecimen.objects.get_or_create(
            inventory=inventory, specimen=specimen,
            defaults={'count': specimen.count})
        url = reverse_lazy('monitoring:inventory',
                           kwargs={'pk': self.kwargs['inventory_pk']})
        return HttpResponseRedirect(url)
inventoryspecimen_add = staff_member_required(
    InventorySpecimenAdd.as_view())


class InventorySpecimenByBarCode(FormView):
    form_class = InventorySpecimenForm
    fields = '__all__'

    def redirect(self, form):
        url = reverse_lazy('monitoring:inventory',
                           kwargs={'pk': form.cleaned_data['inventory'].pk})
        return HttpResponseRedirect(url)

    def form_valid(self, form):
        form.save()
        msg = _('Specimen {specimen} has been added to {inventory} inventory')
        msg = msg.format(specimen=form.instance.specimen.barcode,
                         inventory=form.instance.inventory.made_at)
        messages.add_message(self.request, messages.SUCCESS, msg)
        return self.redirect(form)

    def form_invalid(self, form):
        msg = _('Specimen {specimen} not found or already done.')
        msg = msg.format(specimen=form.data['specimen'])
        messages.add_message(self.request, messages.ERROR, msg)
        return self.redirect(form)


inventoryspecimen_bybarcode = staff_member_required(
    InventorySpecimenByBarCode.as_view())


class InventorySpecimenRemove(View):

    def get(self, request, *args, **kwargs):
        inventory = get_object_or_404(Inventory,
                                      pk=self.kwargs['inventory_pk'])
        specimen = get_object_or_404(Specimen, pk=self.kwargs['specimen_pk'])
        InventorySpecimen.objects.filter(inventory=inventory,
                                         specimen=specimen).delete()
        url = reverse_lazy('monitoring:inventory',
                           kwargs={'pk': self.kwargs['inventory_pk']})
        return HttpResponseRedirect(url)
inventoryspecimen_remove = staff_member_required(
    InventorySpecimenRemove.as_view())


class InventorySpecimenIncrease(View):

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(InventorySpecimen, pk=self.kwargs['pk'])
        obj.count = obj.count + 1
        obj.save()
        url = reverse_lazy('monitoring:inventory',
                           kwargs={'pk': obj.inventory.pk})
        return HttpResponseRedirect(url)
inventoryspecimen_increase = staff_member_required(
    InventorySpecimenIncrease.as_view())


class InventorySpecimenDecrease(View):

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(InventorySpecimen, pk=self.kwargs['pk'])
        obj.count = max(obj.count - 1, 0)
        obj.save()
        url = reverse_lazy('monitoring:inventory',
                           kwargs={'pk': obj.inventory.pk})
        return HttpResponseRedirect(url)
inventoryspecimen_decrease = staff_member_required(
    InventorySpecimenDecrease.as_view())


class ItemLoan(TemplateView):
    template_name = 'monitoring/loan.html'

    def get_context_data(self, **kwargs):
        due_date = date.today() + timedelta(days=settings.LOAN_DURATION)
        defaults = {
            'loan_form': LoanForm(initial={'due_date': due_date}),
            'return_form': ReturnForm,
            'loans': Loan.objects.due(),
            'export_form': ExportLoanForm
        }
        defaults.update(kwargs)
        return super(ItemLoan, self).get_context_data(**defaults)

    def post(self, request, *args, **kwargs):
        context = {}
        if 'do_loan' in request.POST:
            loan_form = LoanForm(data=request.POST)
            if loan_form.is_valid():
                specimen = loan_form.cleaned_data['specimen']
                user = loan_form.cleaned_data['user']
                Loan.objects.create(
                    specimen=specimen,
                    user=user,
                    comments=loan_form.cleaned_data['comments'],
                    due_date=loan_form.cleaned_data['due_date'],
                    by=request.user)
                msg = _('Item {item} has been loaned to {user}')
                msg = msg.format(item=specimen.item, user=user)
                messages.add_message(self.request, messages.SUCCESS, msg)
            else:
                context['loan_form'] = loan_form
        elif 'do_return' in request.POST:
            return_form = ReturnForm(data=request.POST)
            if return_form.is_valid():
                loan = return_form.cleaned_data['loan']
                if loan:
                    loan.mark_returned()
                    msg = _('Item {item} has been returned')
                    msg = msg.format(item=loan.specimen.item)
                    status = messages.SUCCESS
                else:
                    msg = _('Item not found')
                    status = messages.ERROR
                messages.add_message(self.request, status, msg)
            else:
                context['return_form'] = return_form
        return self.render_to_response(self.get_context_data(**context))
loan = staff_member_required(ItemLoan.as_view())


class ExportLoan(CSVExportMixin, View):
    prefix = 'loan'

    def get(self, *args, **kwargs):
        self.form = ExportLoanForm(self.request.GET)
        if self.form.is_valid():
            return self.render_to_csv()
        else:
            msg = _('Error while processing loans export')
            messages.add_message(self.request, messages.ERROR, msg)
            messages.add_message()
            return HttpResponseRedirect(reverse_lazy('monitoring:loan'))

    def get_headers(self):
        self.fields = ['item', 'barcode', 'user', 'loaned at', 'due date',
                       'returned at', 'comments']
        return self.fields

    def get_items(self):
        qs = Loan.objects.order_by('created_at')
        if self.form.cleaned_data['since']:
            qs = qs.filter(created_at__gte=self.form.cleaned_data['since'])
        return qs

    def get_row(self, entry):
        return {
            'item': unicode(entry.specimen.item).encode('utf-8'),
            'barcode': entry.specimen.barcode,
            'user': entry.user.serial.encode('utf-8'),
            'loaned at': entry.created_at,
            'due date': entry.due_date,
            'returned at': entry.returned_at,
            'comments': entry.comments.encode('utf-8')
        }

export_loan = staff_member_required(ExportLoan.as_view())

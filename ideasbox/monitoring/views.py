import csv
import StringIO
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  TemplateView, UpdateView, View)

from .forms import (EntryForm, ExportEntryForm, InventorySpecimenForm,
                    SpecimenForm)
from .models import Entry, Inventory, InventorySpecimen, Specimen, StockItem

user_model = get_user_model()


class EntryView(FormView):
    template_name = 'monitoring/entry.html'
    form_class = EntryForm
    success_url = reverse_lazy('monitoring:entry')

    def form_valid(self, form):
        count = 0
        module = form.cleaned_data['module']
        for serial in form.cleaned_data['serials']:
            try:
                user = user_model.objects.get(serial=serial)
            except user_model.DoesNotExist:
                msg = _('No user found with serial {serial}')
                msg = msg.format(serial=serial)
                messages.add_message(self.request, messages.ERROR, msg)
            else:
                Entry.objects.create(user=user, module=module)
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
        context['entries'] = Entry.objects.all()[:20]
        context['export_form'] = ExportEntryForm()
        return context

entry = staff_member_required(EntryView.as_view())


@staff_member_required
def export_entry(request):
    form = ExportEntryForm(request.GET)
    if form.is_valid():
        out = StringIO.StringIO()
        fields = ['module', 'date']
        fields.extend(settings.MONITORING_ENTRY_EXPORT_FIELDS)
        writer = csv.DictWriter(out, fields)
        writer.writeheader()
        qs = Entry.objects.all()
        if form.cleaned_data['since']:
            qs = qs.filter(created_at__gte=form.cleaned_data['since'])
        for entry in qs:
            row = {'module': entry.module, 'date': entry.created_at}
            for field in settings.MONITORING_ENTRY_EXPORT_FIELDS:
                row[field] = getattr(entry.user, field, None)
            writer.writerow(row)
        out.seek(0)
        response = HttpResponse(out.read())
        filename = 'entries_{id}_{date}'.format(id=settings.IDEASBOX_ID,
                                                date=datetime.now())
        attachment = 'attachment; filename="{name}.csv"'.format(
            name=filename)
        response['Content-Disposition'] = attachment
        response['Content-Type'] = 'text/csv'
        return response


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
inventory_update = staff_member_required(InventoryUpdate.as_view())


class InventoryCreate(CreateView):
    model = Inventory
inventory_create = staff_member_required(InventoryCreate.as_view())


class InventoryDelete(DeleteView):
    model = Inventory
    success_url = reverse_lazy('monitoring:stock')
inventory_delete = staff_member_required(InventoryDelete.as_view())


class StockItemUpdate(UpdateView):
    model = StockItem
    success_url = reverse_lazy('monitoring:stock')
stockitem_update = staff_member_required(StockItemUpdate.as_view())


class StockItemCreate(CreateView):
    model = StockItem
    success_url = reverse_lazy('monitoring:stock')
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
    success_url = reverse_lazy('monitoring:stock')

    def get_initial(self):
        item = get_object_or_404(StockItem, pk=self.kwargs['item_pk'])
        return {'item': item}
specimen_create = staff_member_required(SpecimenCreate.as_view())


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
        msg = _('Specimen {specimen} has not been found')
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

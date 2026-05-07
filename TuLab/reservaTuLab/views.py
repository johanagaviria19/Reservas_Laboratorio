from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm, ReservaStatusForm
import csv
from django.http import HttpResponse

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        # Los docentes solo ven sus propias reservas
        # Los administradores ven todas
        if self.request.user.is_superuser:
            queryset = Reserva.objects.all()
        else:
            queryset = Reserva.objects.filter(usuario=self.request.user)
        
        # Filtros
        laboratorio = self.request.GET.get('laboratorio')
        fecha = self.request.GET.get('fecha')
        
        if laboratorio:
            queryset = queryset.filter(laboratorio__icontains=laboratorio)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['total_reservas'] = Reserva.objects.count()
            context['pendientes'] = Reserva.objects.filter(estado='pendiente').count()
            context['aprobadas'] = Reserva.objects.filter(estado='aprobada').count()
        return context

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservaTuLab/reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Reserva creada con éxito y pendiente de aprobación.")
        return super().form_valid(form)

class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservaTuLab/reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        reserva = self.get_object()
        # Solo el dueño puede editar y solo si está pendiente
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

    def form_valid(self, form):
        messages.success(self.request, "Reserva actualizada con éxito.")
        return super().form_valid(form)

class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_confirm_delete.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        reserva = self.get_object()
        # Solo el dueño puede borrar y solo si está pendiente
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Reserva eliminada con éxito.")
        return super().delete(request, *args, **kwargs)

class ReservaStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaStatusForm
    template_name = 'reservaTuLab/reserva_status_form.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        # Solo superusuarios (Administradores) pueden cambiar el estado
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, f"Estado de la reserva actualizado a {form.instance.get_estado_display()}.")
        return super().form_valid(form)

def exportar_reservas_csv(request):
    if not request.user.is_superuser:
        return redirect('reserva_list')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Laboratorio', 'Fecha', 'Inicio', 'Fin', 'Estado', 'Motivo'])
    
    reservas = Reserva.objects.all()
    for r in reservas:
        writer.writerow([r.usuario.username, r.laboratorio, r.fecha, r.hora_inicio, r.hora_fin, r.get_estado_display(), r.motivo])
        
    return response

from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Count
from .models import Reserva

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        queryset = Reserva.objects.all()
        # Filtros
        laboratorio = self.request.GET.get('laboratorio')
        fecha = self.request.GET.get('fecha')
        
        if laboratorio:
            queryset = queryset.filter(laboratorio__icontains=laboratorio)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        # Si no es staff, solo ve sus propias reservas
        if not self.request.user.is_staff:
            queryset = queryset.filter(usuario=self.request.user)
            
        return queryset.order_by('-fecha', '-hora_inicio')

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_form.html'
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_form.html'
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo', 'estado']
    success_url = reverse_lazy('reserva_list')

    def get_fields(self):
        # Si no es staff, no puede cambiar el estado
        fields = super().get_fields()
        if not self.request.user.is_staff:
            if 'estado' in fields:
                fields.remove('estado')
        return fields

    def test_func(self):
        reserva = self.get_object()
        # El Administrador puede editar cualquier reserva
        if self.request.user.is_staff:
            return True
        # El Docente solo edita sus propias reservas y solo si están "Pendientes"
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reservaTuLab/reserva_confirm_delete.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        reserva = self.get_object()
        if self.request.user.is_staff:
            return True
        return reserva.usuario == self.request.user and reserva.estado == 'pendiente'

class EstadisticasView(LoginRequiredMixin, TemplateView):
    template_name = 'reservaTuLab/estadisticas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Laboratorios más reservados
        stats = Reserva.objects.values('laboratorio').annotate(
            total=Count('id')
        ).order_by('-total')
        context['estadisticas'] = stats
        return context

from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'usuario', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha', 'laboratorio')
    search_fields = ('laboratorio', 'usuario__username', 'motivo')
    readonly_fields = ('fecha_creacion',)
    
    # Permitir al administrador cambiar el estado fácilmente
    actions = ['aprobar_reservas', 'rechazar_reservas']

    def aprobar_reservas(self, request, queryset):
        queryset.update(estado='aprobada')
    aprobar_reservas.short_description = "Marcar seleccionadas como Aprobadas"

    def rechazar_reservas(self, request, queryset):
        queryset.update(estado='rechazada')
    rechazar_reservas.short_description = "Marcar seleccionadas como Rechazadas"

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    laboratorio = models.CharField(max_length=100, verbose_name="Laboratorio")
    fecha = models.DateField(verbose_name="Fecha de la reserva")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de finalización")
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente',
        verbose_name="Estado"
    )
    motivo = models.TextField(verbose_name="Motivo de la reserva")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"{self.laboratorio} - {self.fecha} ({self.usuario.username})"

    def clean(self):
        # Validar que la hora de inicio sea antes que la hora de fin
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        # Validar que la fecha no sea en el pasado
        if self.fecha and self.fecha < timezone.now().date():
            raise ValidationError("No se pueden realizar reservas para fechas pasadas.")

        # Validar conflictos de horario en el mismo laboratorio
        # Se buscan reservas aprobadas o pendientes que se solapen
        conflictos = Reserva.objects.filter(
            laboratorio=self.laboratorio,
            fecha=self.fecha
        ).exclude(pk=self.pk).exclude(estado='rechazada')

        # Lógica de solapamiento: (InicioA < FinB) AND (FinA > InicioB)
        for conflicto in conflictos:
            if (self.hora_inicio < conflicto.hora_fin) and (self.hora_fin > conflicto.hora_inicio):
                # Obtener otras reservas del día para informar horarios ocupados
                reservas_dia = Reserva.objects.filter(
                    laboratorio=self.laboratorio,
                    fecha=self.fecha
                ).exclude(pk=self.pk).exclude(estado='rechazada').order_by('hora_inicio')
                
                horarios_ocupados = ", ".join([f"{r.hora_inicio.strftime('%H:%M')} - {r.hora_fin.strftime('%H:%M')}" for r in reservas_dia])
                
                raise ValidationError(
                    f"Conflicto de horario: El laboratorio {self.laboratorio} ya tiene una reserva "
                    f"de {conflicto.hora_inicio.strftime('%H:%M')} a {conflicto.hora_fin.strftime('%H:%M')}. "
                    f"Horarios ocupados para este día: {horarios_ocupados}. Por favor, elija un horario fuera de estos rangos."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

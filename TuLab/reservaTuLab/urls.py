from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='reserva_list'),
    path('nueva/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('editar/<int:pk>/', views.ReservaUpdateView.as_view(), name='reserva_update'),
    path('eliminar/<int:pk>/', views.ReservaDeleteView.as_view(), name='reserva_delete'),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
]

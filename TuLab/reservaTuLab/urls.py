from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='reserva_list'),
    path('nueva/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('editar/<int:pk>/', views.ReservaUpdateView.as_view(), name='reserva_update'),
    path('eliminar/<int:pk>/', views.ReservaDeleteView.as_view(), name='reserva_delete'),
    path('estado/<int:pk>/', views.ReservaStatusUpdateView.as_view(), name='reserva_status_update'),
    path('exportar-csv/', views.exportar_reservas_csv, name='exportar_csv'),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='reservaTuLab/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

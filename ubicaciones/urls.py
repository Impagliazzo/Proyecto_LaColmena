from django.urls import path

from . import views

app_name = 'ubicaciones'

urlpatterns = [
    path('api/provincias/', views.provincias_sugerencias, name='provincias_sugerencias'),
    path('api/localidades/', views.localidades_sugerencias, name='localidades_sugerencias'),
    path('api/distritos/', views.distritos_sugerencias, name='distritos_sugerencias'),
]

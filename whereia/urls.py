"""
URL configuration for whereia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('comercio/<slug:slug>/', views.perfil_comercio, name='perfil_comercio'),
    path('comercio/<slug:slug>/resena/', views.dejar_resena, name='dejar_resena'),
    path('resena/<int:resena_id>/responder/', views.responder_resena, name='responder_resena'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/editar/<slug:slug>/', views.panel_editar, name='panel_editar'),
    path('panel/crear-comercio/', views.panel_crear_comercio, name='panel_crear_comercio'),

]

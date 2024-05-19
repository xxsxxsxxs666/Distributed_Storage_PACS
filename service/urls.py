"""service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from server import views as server_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('read/<str:patient_id>/<int:file_index>/', server_views.read_dicom_hadoop, name='read_dicom_hadoop'),
    path('patientdcm/<str:patient_id>/', server_views.get_patient_dcm_list_hadoop, name='get_patient_dcm_list_hadoop'),
    path('copy_newpatient_to_patient/', server_views.copy_newpatient_to_patient, name='copy_newpatient_to_patient'),
    path('get_all_patients/', server_views.get_all_patients_hadoop, name='get_all_patients_hadoop'),
]
from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('registrationform', views.savepersondetails.as_view(), name = 'registrationform'),
    path('signup', views.signupPage, name='signupPage'),
    path('login', views.loginPage, name='loginPage'),
    path('logout', views.logoutPage, name='logoutPage'),
    path('Vieweditgatepass', views.listResume.as_view(), name='Vieweditgatepass'),
    path('updategetpass', views.viewResume.as_view(), name='updategetpass'),
    path('exportdata', views.exportdata.as_view(), name='exportdata'),
    path('exporttoexcel', views.exporttoexcel.as_view(), name='exporttoexcel'),
    path('updatedetails/<str:vehicle_no>/', views.updatedetails.as_view(), name='updatedetails'),
    path('updateregdetails/<str:vehicle_no>/', views.updateregdetails.as_view(), name='updateregdetails'),
    path('forgetpassword', views.forgotpasswordview.as_view(), name='forgetpassword'),
    path('tally', views.tally.as_view(), name='tally')
] 

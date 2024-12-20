from django.urls import path
from bazyy_app import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dodaj_pracownika/', views.dodaj_pracownika_view, name='dodaj_pracownika'),
    path('strona_po_zalogowaniu/', views.strona_po_zalogowaniu, name='strona_po_zalogowaniu'),
    path('zamowienie_paliwa/', views.zamowienie_paliwa_view, name='zamowienie_paliwa'),
    path('success/', views.success_view, name='success'),
    path('zatwierdz_zamowienie/<int:zamowienie_id>/', views.zatwierdz_zamowienie_view, name='zatwierdz_zamowienie'),
    path('wyloguj/', views.wyloguj_view, name='wyloguj'),
    path('aktualne_zamowienia/', views.aktualne_zamowienia_view, name='aktualne_zamowienia'),
    path('historia_zamowien/', views.historia_zamowien_view, name='historia_zamowien'),
    path('przyjmij_dostawe/<int:zamowienie_id>/', views.przyjmij_dostawe_view, name='przyjmij_dostawe'),
    path('szczegoly_zamowienia/<int:zamowienie_id>/', views.szczegoly_zamowienia_view, name='szczegoly_zamowienia'),
    path('przyjeto_dostawe/<int:zamowienie_id>/', views.przyjeto_dostawe_view, name='przyjeto_dostawe'),
    path('kierowcy/', views.kierowcy_view, name='kierowcy'),
    path('kierowcy/trasy/<int:kierowca_id>/', views.kierowca_trasy_view, name='kierowca_trasy'),
    path('lista_cystern/', views.lista_cystern_view, name='lista_cystern'),
    path('zmien_dane_cysterny/<int:id_cysterny>/', views.zmien_dane_cysterny_view, name='zmien_dane_cysterny'),
    path('przyjmij_dostawe/<int:zamowienie_id>/', views.przyjmij_dostawe_view, name='przyjmij_dostawe'),
]

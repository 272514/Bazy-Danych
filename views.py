from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pracownik, Zamowienie, Kierowca, Cysterna, CzasTrasyKierowcow
from .forms import PracownikForm, ZamowienieForm, CysternaForm
from django.contrib.auth import logout
from django.utils import timezone
from django.core.paginator import Paginator
import random

def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        haslo = request.POST.get('haslo')

        try:
            pracownik = Pracownik.objects.get(login=login)

            if pracownik.haslo != haslo:
                messages.error(request, 'Nieprawidłowe hasło.')
                return redirect('login')

            request.session['id_pracownika'] = pracownik.id_pracownika
            request.session['stanowisko'] = pracownik.stanowisko
            request.session['id_stacji'] = pracownik.id_stacji

            
            return redirect('strona_po_zalogowaniu')

        except Pracownik.DoesNotExist:
            messages.error(request, 'Nie znaleziono użytkownika.')
            return redirect('login')

    return render(request, 'login.html')


def dodaj_pracownika_view(request):
    if request.method == 'POST':
        form = PracownikForm(request.POST)
        if form.is_valid():
            id_stacji_kierownika = request.session.get('id_stacji')

            if id_stacji_kierownika:
                nowy_pracownik = form.save(commit=False)
                nowy_pracownik.id_stacji = id_stacji_kierownika
                nowy_pracownik.stanowisko = 'Pracownik'
                nowy_pracownik.save()

                messages.success(request, 'Pracownik został dodany pomyślnie!')
                return redirect('strona_po_zalogowaniu')
            else:
                messages.error(request, 'Nie znaleziono przypisanej stacji dla kierownika.')
                return redirect('dodaj_pracownika')

    else:
        form = PracownikForm()

    return render(request, 'dodaj_pracownika.html', {'form': form})


def success_view(request):
    return render(request, 'success.html')

def strona_po_zalogowaniu(request):
    id_pracownika = request.session.get('id_pracownika')
    stanowisko = request.session.get('stanowisko')
    id_stacji = request.session.get('id_stacji')

    if id_pracownika:
        try:
            pracownik = Pracownik.objects.get(id_pracownika=id_pracownika)

            komunikat = f"Witaj, {pracownik.stanowisko}u!"

            if stanowisko == 'Manager':
                return render(request, 'zalogowano_manager.html', {'komunikat': komunikat})
            elif stanowisko == 'Kierownik':
                zamowienia = Zamowienie.objects.filter(status='Do zatwierdzenia', id_stacji=id_stacji)
                cysterny = Cysterna.objects.all()
                return render(request, 'zalogowano_kierownik.html', {
                    'komunikat': komunikat, 
                    'id_stacji': id_stacji, 
                    'zamowienia': zamowienia,
                    'cysterny': cysterny
                })
            else:
                return render(request, 'zalogowano_pracownik.html', {'komunikat': komunikat, 'id_stacji': id_stacji})

        except Pracownik.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

def zamowienie_paliwa_view(request):
    id_pracownika = request.session.get('id_pracownika')

    if not id_pracownika:
        messages.error(request, 'Nie znaleziono zalogowanego pracownika.')
        return redirect('login')

    stanowisko = request.session.get('stanowisko')

    if request.method == 'POST':
        form = ZamowienieForm(request.POST)
        if form.is_valid():
            rodzaj_paliwa = form.cleaned_data['rodzaj_paliwa']
            ilosc_paliwa = form.cleaned_data['ilosc_paliwa']
            uwagi = form.cleaned_data['uwagi']

            if stanowisko == 'Kierownik':
                wolny_kierowca = Kierowca.objects.filter(status='Wolny').order_by('?').first()
                if not wolny_kierowca:
                    messages.error(request, 'Brak dostępnych wolnych kierowców.')
                    return redirect('zamowienie_paliwa')

                wolna_cysterna = Cysterna.objects.filter(status='Wolna', pojemnosc__gte=ilosc_paliwa).order_by('?').first()
                if not wolna_cysterna:
                    messages.error(request, 'Brak dostępnych cystern o wystarczającej pojemności.')
                    return redirect('zamowienie_paliwa')

                wolny_kierowca.status = 'W trasie'
                wolna_cysterna.status = 'Zajęta'
                wolny_kierowca.save()
                wolna_cysterna.save()

                status = 'W trakcie'

            else:
                wolny_kierowca = None
                wolna_cysterna = None
                status = 'Do zatwierdzenia'

            data_zamowienia = timezone.now()
            id_stacji = request.session.get('id_stacji')

            try:
                zamowienie = Zamowienie.objects.create(
                    rodzaj_paliwa=rodzaj_paliwa,
                    ilosc_paliwa=ilosc_paliwa,
                    id_kierowcy=wolny_kierowca.id_kierowcy if wolny_kierowca else None,
                    id_cysterny=wolna_cysterna.id_cysterny if wolna_cysterna else None,
                    id_pracownika=id_pracownika,
                    id_stacji=id_stacji,
                    data_zamowienia=data_zamowienia,
                    status=status,
                    uwagi=uwagi
                )

                if stanowisko == 'Kierownik':
                    czas_trasy = CzasTrasyKierowcow.objects.create(
                        id_kierowcy=wolny_kierowca.id_kierowcy,
                        id_cysterny=wolna_cysterna.id_cysterny,
                        id_zamowienia=zamowienie.id_zamowienia,
                        czas_rozpoczecia=data_zamowienia,
                        id_stacji=id_stacji
                    )
                    czas_trasy.numer_rejestracyjny_cysterny = wolna_cysterna.numer_rejestracyjny
                    czas_trasy.save()

            except Exception as e:
                messages.error(request, f'Błąd przy zapisie zamówienia: {str(e)}')

            messages.success(request, 'Zamówienie zostało złożone pomyślnie!')
            return redirect('success')

    else:
        form = ZamowienieForm()

    return render(request, 'zamowienie_paliwa.html', {'form': form})

def zatwierdz_zamowienie_view(request, zamowienie_id):
    zamowienie = get_object_or_404(Zamowienie, id_zamowienia=zamowienie_id)

    id_pracownika = request.session.get('id_pracownika')
    if not id_pracownika:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login')

    stanowisko = request.session.get('stanowisko')
    if stanowisko != 'Kierownik':
        messages.error(request, 'Tylko kierownik może zatwierdzać zamówienia.')
        return redirect('strona_po_zalogowaniu')

    if request.method == 'POST':
        wolny_kierowca = Kierowca.objects.filter(status='Wolny').order_by('?').first()
        if not wolny_kierowca:
            messages.error(request, 'Brak dostępnych wolnych kierowców.')
            return redirect('zatwierdz_zamowienie', zamowienie_id=zamowienie.id_zamowienia)

        wolna_cysterna = Cysterna.objects.filter(status='Wolna', pojemnosc__gte=zamowienie.ilosc_paliwa).order_by('?').first()
        if not wolna_cysterna:
            messages.error(request, 'Brak dostępnych cystern o wystarczającej pojemności.')
            return redirect('zatwierdz_zamowienie', zamowienie_id=zamowienie.id_zamowienia)

        zamowienie.status = 'W trakcie'
        zamowienie.id_kierowcy = wolny_kierowca.id_kierowcy
        zamowienie.id_cysterny = wolna_cysterna.id_cysterny
        zamowienie.save()

        czas_trasy = CzasTrasyKierowcow.objects.create(
            id_kierowcy=wolny_kierowca.id_kierowcy,
            id_cysterny=wolna_cysterna.id_cysterny,
            id_zamowienia=zamowienie.id_zamowienia,
            czas_rozpoczecia=timezone.now(),
            id_stacji=zamowienie.id_stacji
        )
        czas_trasy.numer_rejestracyjny_cysterny = wolna_cysterna.numer_rejestracyjny
        czas_trasy.save()

        wolny_kierowca.status = 'W trasie'
        wolna_cysterna.status = 'Zajęta'
        wolny_kierowca.save()
        wolna_cysterna.save()

        messages.success(request, f"Zamówienie {zamowienie.id_zamowienia} zostało zatwierdzone i przypisano kierowcę oraz cysternę.")
        return redirect('strona_po_zalogowaniu')

    return render(request, 'zatwierdz_zamowienie.html', {'zamowienie': zamowienie})

    
def wyloguj_view(request):
    logout(request)
    return redirect('login')

def historia_zamowien_view(request):
    id_pracownika = request.session.get('id_pracownika')
    if not id_pracownika:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login')

    id_stacji = request.session.get('id_stacji')

    zamowienia = Zamowienie.objects.filter(status='Zrealizowane', id_stacji=id_stacji)

    for zamowienie in zamowienia:
        zamowienie.kierowca = Kierowca.objects.get(id_kierowcy=zamowienie.id_kierowcy)
        zamowienie.cysterna = Cysterna.objects.get(id_cysterny=zamowienie.id_cysterny)

    return render(request, 'historia_zamowien.html', {'zamowienia': zamowienia})


def aktualne_zamowienia_view(request):
    id_pracownika = request.session.get('id_pracownika')
    if not id_pracownika:
        messages.error(request, 'Nie jesteś zalogowany.')
        return redirect('login')

    id_stacji = request.session.get('id_stacji')

    zamowienia = Zamowienie.objects.filter(status='W trakcie', id_stacji=id_stacji)

    for zamowienie in zamowienia:
        zamowienie.kierowca = Kierowca.objects.get(id_kierowcy=zamowienie.id_kierowcy)
        zamowienie.cysterna = Cysterna.objects.get(id_cysterny=zamowienie.id_cysterny)

    return render(request, 'aktualne_zamowienia.html', {'zamowienia': zamowienia})


def przyjmij_dostawe_view(request, zamowienie_id):
    zamowienie = get_object_or_404(Zamowienie, id_zamowienia=zamowienie_id)

    if zamowienie.status != 'W trakcie':
        messages.error(request, 'Zamówienie nie jest w trakcie realizacji.')
        return redirect('aktualne_zamowienia')

    zamowienie.status = 'Zrealizowane'
    zamowienie.data_realizacji = timezone.now()
    zamowienie.save()

    przejechana_dlugosc = round(random.randint(30, 55))

    czas_trasy = CzasTrasyKierowcow.objects.get(id_zamowienia=zamowienie.id_zamowienia)
    
    czas_trasy.przejechana_dlugosc = przejechana_dlugosc

    czas_trasy.czas_zakonczenia = timezone.now()

    if czas_trasy.czas_rozpoczecia and czas_trasy.czas_zakonczenia:
        czas_trasy.calkowity_czas = (czas_trasy.czas_zakonczenia - czas_trasy.czas_rozpoczecia).total_seconds() / 60.0

    czas_trasy.save()

    if zamowienie.id_kierowcy:
        kierowca = Kierowca.objects.get(id_kierowcy=zamowienie.id_kierowcy)
        kierowca.status = 'Wolny'
        kierowca.save()

    if zamowienie.id_cysterny:
        cysterna = Cysterna.objects.get(id_cysterny=zamowienie.id_cysterny)
        cysterna.status = 'Wolna'
        cysterna.save()
    
    messages.success(request, "Dostawa została przyjęta i zrealizowana.")
    return redirect('strona_po_zalogowaniu')

def szczegoly_zamowienia_view(request, zamowienie_id):
    zamowienie = get_object_or_404(Zamowienie, id_zamowienia=zamowienie_id)

    kierowca = None
    cysterna = None
    if zamowienie.id_kierowcy:
        kierowca = Kierowca.objects.get(id_kierowcy=zamowienie.id_kierowcy)
    if zamowienie.id_cysterny:
        cysterna = Cysterna.objects.get(id_cysterny=zamowienie.id_cysterny)

    if request.method == 'POST':
        if 'potwierdz' in request.POST:
            try:
                zamowienie.status = 'Zrealizowane'
                zamowienie.data_realizacji = timezone.now()
                zamowienie.save()

                czas_trasy = CzasTrasyKierowcow.objects.filter(id_zamowienia=zamowienie_id).first()
                if czas_trasy:
                    czas_trasy.czas_zakonczenia = timezone.now()

                    if czas_trasy.czas_rozpoczecia:
                        czas_trasy.calkowity_czas = (czas_trasy.czas_zakonczenia - czas_trasy.czas_rozpoczecia).total_seconds() / 60.0
                    czas_trasy.save()

                if kierowca:
                    kierowca.status = 'Wolny'
                    kierowca.save()

                if cysterna:
                    cysterna.status = 'Wolna'
                    cysterna.save()

                messages.success(request, f"Zamówienie {zamowienie.id_zamowienia} zostało zrealizowane.")
                return redirect('strona_po_zalogowaniu')
            except Exception as e:
                messages.error(request, f"Wystąpił błąd: {str(e)}")

    return render(request, 'szczegoly_zamowienia.html', {
        'zamowienie': zamowienie,
        'kierowca': kierowca,
        'cysterna': cysterna
    })

def przyjeto_dostawe_view(request, zamowienie_id):
    zamowienie = get_object_or_404(Zamowienie, id_zamowienia=zamowienie_id)

    zamowienie.kierowca = Kierowca.objects.get(id_kierowcy=zamowienie.id_kierowcy)
    zamowienie.cysterna = Cysterna.objects.get(id_cysterny=zamowienie.id_cysterny)

    return render(request, 'przyjeto_dostawe.html', {'zamowienie': zamowienie})

def kierowcy_view(request):
    kierowcy = Kierowca.objects.all().order_by('id_kierowcy')  
    
    paginator = Paginator(kierowcy, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kierowcy.html', {'page_obj': page_obj})


def kierowca_trasy_view(request, kierowca_id):
    kierowca = get_object_or_404(Kierowca, id_kierowcy=kierowca_id)

    trasy = CzasTrasyKierowcow.objects.filter(id_kierowcy=kierowca_id)

    trasy_zakonczone = []
    for trasa in trasy:
        zamowienie = Zamowienie.objects.get(id_zamowienia=trasa.id_zamowienia)
        
        if zamowienie.status == 'Zrealizowane':
            cysterna = Cysterna.objects.get(id_cysterny=trasa.id_cysterny)

            trasa.numer_rejestracyjny_cysterny = cysterna.numer_rejestracyjny

            if trasa.czas_zakonczenia is None:
                trasa.czas_zakonczenia = timezone.now()
            if trasa.calkowity_czas is None and trasa.czas_zakonczenia:
                trasa.calkowity_czas = (trasa.czas_zakonczenia - trasa.czas_rozpoczecia).total_seconds() / 60.0

            trasy_zakonczone.append(trasa)

    return render(request, 'kierowca_trasy.html', {'kierowca': kierowca, 'trasy': trasy_zakonczone})

def lista_cystern_view(request):
    cysterny = Cysterna.objects.all()

    return render(request, 'lista_cystern.html', {'cysterny': cysterny})

def zmien_dane_cysterny_view(request, id_cysterny):
    cysterna = get_object_or_404(Cysterna, id_cysterny=id_cysterny)

    if request.method == 'POST':
        form = CysternaForm(request.POST, instance=cysterna)
        if form.is_valid():
            form.save()
            messages.success(request, "Dane cysterny zostały zaktualizowane!")
            return redirect('lista_cystern')
        else:
            messages.error(request, "Wystąpił błąd podczas aktualizacji danych cysterny.")
    else:
        form = CysternaForm(instance=cysterna)

    return render(request, 'zmien_dane_cysterny.html', {'form': form, 'cysterna': cysterna})

from django.db import models

class Pracownik(models.Model):
    id_pracownika = models.IntegerField(primary_key=True)
    id_stacji = models.IntegerField(null=True, blank=True)
    stanowisko = models.CharField(max_length=255, null=True, blank=True)
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    numer_kontaktowy = models.CharField(max_length=15, null=True, blank=True)
    haslo = models.CharField(max_length=255)

    class Meta:
        db_table = 'pracownicy_stacji'

    def __str__(self):
        return f"{self.imie} {self.nazwisko} ({self.stanowisko})"

class CzasTrasyKierowcow(models.Model):
    id_czas_trasy = models.AutoField(primary_key=True)
    id_kierowcy = models.IntegerField(null=True, blank=True)
    id_cysterny = models.IntegerField(null=True, blank=True)
    id_stacji = models.IntegerField(null=True, blank=True)
    id_zamowienia = models.IntegerField(null=True, blank=True)

    czas_rozpoczecia = models.DateTimeField(null=True, blank=True)
    czas_zakonczenia = models.DateTimeField(null=True, blank=True) 
    calkowity_czas = models.FloatField(null=True, blank=True)
    przejechana_dlugosc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'czas_trasy_kierowcow'

    def __str__(self):
        return f"Trasa {self.id_czas_trasy}"

class Stacja(models.Model):
    id_stacji = models.AutoField(primary_key=True)
    adres = models.CharField(max_length=255, null=True, blank=True)
    kierownik = models.ForeignKey(Pracownik, on_delete=models.CASCADE, related_name='stacje', null=True, blank=True)
    numer_kontaktowy = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = 'stacje'

    def __str__(self):
        return self.adres

class Kierowca(models.Model):
    id_kierowcy = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    numer_kontaktowy = models.CharField(max_length=15, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'kierowcy'

    def __str__(self):
        return f"{self.imie} {self.nazwisko} ({self.status})"


class Cysterna(models.Model):
    id_cysterny = models.AutoField(primary_key=True)
    numer_rejestracyjny = models.CharField(max_length=50)
    pojemnosc = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, null=True, blank=True)
    data_przegladu = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cysterny'

    def __str__(self):
        return f'{self.numer_rejestracyjny} - {self.pojemnosc}L'



class Zamowienie(models.Model):
    id_zamowienia = models.AutoField(primary_key=True)
    rodzaj_paliwa = models.CharField(max_length=50)
    ilosc_paliwa = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    id_kierowcy = models.IntegerField(null=True, blank=True)
    id_cysterny = models.IntegerField(null=True, blank=True)
    id_pracownika = models.IntegerField(null=True, blank=True)
    id_stacji = models.IntegerField(null=True, blank=True)
    data_zamowienia = models.DateTimeField(null=True, blank=True)
    data_realizacji = models.DateTimeField(null=True, blank=True)
    uwagi = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'zamowienia'

    def __str__(self):
        return f"Zamówienie {self.id_zamowienia}"

# Universal Game Ambilight voor Home Assistant

Werkt met iedere game, film, video of desktop op de primaire monitor. Fullscreen en borderless worden ondersteund. Het programma controleert geen game-processen.

Het programma leest alleen dunne randstroken van het beeld. Daardoor blijft de belasting laag en reageren de lampen snel.

## Vereisten

- Windows 10 of 11
- Python 3.10 of nieuwer
- Home Assistant met RGB-lampen
- Een long-lived access token in Home Assistant

## Installatie op Windows

```powershell
py -m pip install mss numpy requests
copy config.example.json config.json
notepad config.json
py ambilight.py
```

Vul in `config.json` je Home Assistant-adres, token en de drie lamp-entiteiten in. Gebruik bijvoorbeeld `http://192.168.2.50:8123`. Gebruik geen token uit dit openbare project. Maak je eigen token aan in Home Assistant via je profiel, beveiliging en Long-Lived Access Tokens.

## Games toevoegen

Voeg de exacte procesnaam toe onder `games`. Controleer die naam in PowerShell met:

```powershell
tasklist | findstr /I "DayZ Wardogs"
```

De standaardinstelling leest 10 keer per seconde. Alleen duidelijke kleurverschillen sturen een update naar Home Assistant. Verlaag `capture_fps` naar 6 op een oudere pc.

`left` krijgt de linker rand, `right` de rechter rand en `center` de bovenste middenrand.

## Veiligheid

`config.json` hoort nooit op GitHub te staan. Deze repository bevat alleen `config.example.json`. Deel je Home Assistant-token nooit.

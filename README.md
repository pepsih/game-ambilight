# Universal Game Ambilight voor Home Assistant

Supports Wardogs at 1920x1080, DayZ at 2560x1440, and future games through the `games` section in `config.json`. The program captures the primary monitor, analyzes left, right and center colors, and updates the three Home Assistant lights.

Dit programma maakt van je primaire monitor een eenvoudige Ambilight voor Home Assistant. Het werkt met meerdere games. De lampen links, rechts en in het midden krijgen kleuren uit het beeld.

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

De voorbeeldconfiguratie bevat Wardogs en DayZ. Het programma start alleen kleurupdates wanneer een van deze processen actief is.

## Veiligheid

`config.json` hoort nooit op GitHub te staan. Deze repository bevat alleen `config.example.json`. Deel je Home Assistant-token nooit.

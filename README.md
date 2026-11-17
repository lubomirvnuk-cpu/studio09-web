# studio09.sk

Súbory webu studio09.sk. Web sa zverejňuje automaticky cez GitHub Pages.

- `nastroje/*/index.html` a `prirucka/index.html` sú kópie titulky (pekné adresy nástrojov a príručky) – pri každej zmene titulky ich treba prekopírovať.

## Podstránky áut (`auta/`)
- Údaje áut sú len na jednom mieste: zoznam `CARS` v `index.html` (pole `slug` = adresa podstránky, `was` = pôvodná cena, `det` = údaje navyše a text výbavy).
- Fotky: `auta/<slug>/foto/01.jpg…` (+ zmenšené `foto/m/`). Pripravia sa príkazom
  `python3 auta/vyrob.py --fotky <slug> <zložka s originálmi> IMG_1,IMG_2,…` (poradie = poradie na webe).
- Po každej zmene v `CARS` spustiť `python3 auta/vyrob.py` – prerobí všetky podstránky zo šablóny `auta/_sablona.html`.

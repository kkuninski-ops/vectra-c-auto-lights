# KiCad 10 — Vectra C Auto Lights

## Файлове

| Файл | Описание |
|------|----------|
| `vectra-auto-lights.kicad_pro` | KiCad проект (design rules, net classes) |
| `vectra-auto-lights.kicad_sch` | Схема (генерирана от `generate_kicad.py`) |
| `vectra-auto-lights.kicad_pcb` | PCB layout (120×80mm, THT компоненти) |
| `generate_kicad.py` | Python скрипт — генерира `.kicad_sch` |

## Генериране на схемата

```bash
cd hardware/kicad
python3 generate_kicad.py
# → vectra-auto-lights.kicad_sch
```

## Отваряне в KiCad 10

1. Отвори `vectra-auto-lights.kicad_pro` с KiCad 10
2. **Schematic Editor** → Tools → Update Symbols from Library
3. Схемата използва **net labels** за всички връзки —
   свежи символите визуално, ако е необходимо
4. **PCB Editor** → отвори `vectra-auto-lights.kicad_pcb`
5. Tools → Update PCB from Schematic (за синхронизиране)

## PCB

- Размер: **120 × 80 mm**
- 2 слоя (F.Cu сигнали, B.Cu GND pour)
- Монтажни отвори: 4× M3 в ъглите
- Всички компоненти THT (during-hole) — лесен ръчен монтаж

## Design Rules

| Параметър | Стойност |
|-----------|----------|
| Min track width | 0.2 mm |
| Power tracks | 0.5 mm |
| Min clearance | 0.2 mm |
| Via diameter | 0.8 mm / drill 0.4 mm |
| Power via | 1.0 mm / drill 0.6 mm |

## Конектори (JST-XH 2.54mm)

| Реф | Пинове | Функция |
|-----|--------|---------|
| J1 | 3 | KL30, GND, VBAT |
| J2 | 4 | KL18, AUTO, UNLOCK, GND |
| J3 | 5 | BCM_XENON, BCM_GABARI, BCM_FOG, BCM_ILLUM, GND |
| J4 | 5 | XENON_OUT, GABARI_OUT, FOG_OUT, ILLUM_OUT, GND |
| J5 | 2 | +5V → ESP32 VIN, GND |

## Gerber файлове

```bash
# В KiCad PCB Editor:
File → Fabrication Outputs → Gerbers
Output dir: gerbers/
```

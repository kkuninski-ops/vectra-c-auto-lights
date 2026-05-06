# Vectra C Auto Lights Controller

Автоматичен контролер за управление на светлините на **Opel Vectra C 2008** с ксенон D1S.
MCU: **ESP32** с вграден Bluetooth (BLE).

## Функции

Всички функции работят **само при AUTO позиция** на копчето за светлини.
При ръчни позиции (0 / габарити / ниски) — factory поведение, контролерът не се намесва.

| Режим | Условие | Светлини |
|-------|---------|---------|
| **Welcome** | Отключване без ключ | конфигурируемо (габарити / мъгла / ксенон) |
| **ACC** | Контакт без двигател | конфигурируемо |
| **DRL** | Двигател работи | ксенон + габарити |
| **Goodbye** | Двигател спира | конфигурируемо |

### DRL — защо така

- Ксенонът светва в момента в който алтернаторът вдига напрежението над 13.2V
- При всяко палене се вижда пълният студен старт на ксенона (синьо/лилаво → бяло) + нивелиране
- Нивелирането е независимо от нашия контролер — задейства се от сигнала на двигателя

### Конфигурация от телефон (BLE)

Свържи се с **"Vectra Auto Lights"** от BLE Terminal приложение и пиши команди:

```
set welcome.lights=GABARI+FOG
set welcome.time=30
set goodbye.lights=GABARI
set goodbye.time=60
set acc.lights=GABARI
set acc.enabled=1
status
reset
```

Вижте [docs/ble-commands.md](docs/ble-commands.md) за пълен списък.

## Хардуер накратко

- **MCU:** ESP32 DevKit v1
- **Ксенон:** IRF4905 P-MOSFET + 2N7000 драйвер (high-side, паралелно на BCM)
- **Габарити / Мъгла:** 12V реле × 2 (паралелно на BCM)
- **Входове:** 3× PC817 оптрон (ACC, AUTO, Unlock) + ADC делител (Vbat)
- **Захранване:** LM7805 от KL30 (постоянно)
- **Защити:** TVS (P6KE15A), реверсна диода, watchdog (ESP32 вграден)

## Структура на репото

```
vectra-c-auto-lights/
├── README.md
├── hardware/
│   └── schematic.md          ← ASCII схема + BOM
├── firmware/
│   ├── platformio.ini        ← PlatformIO конфигурация
│   └── src/
│       ├── main.cpp          ← setup() и loop()
│       ├── common.h          ← споделени константи
│       ├── config.h/cpp      ← конфигурация + NVS съхранение
│       ├── inputs.h/cpp      ← четене на входове + ADC
│       ├── outputs.h/cpp     ← управление на изходи
│       ├── state_machine.h/cpp ← главна логика
│       └── ble_config.h/cpp  ← Bluetooth конфигурация
├── docs/
│   ├── pinout.md             ← точки за свързване в колата
│   └── ble-commands.md       ← BLE команди
└── wiki/                     ← knowledge base
```

## Quick start

1. Инсталирай [PlatformIO](https://platformio.org/)
2. Отвори папка `firmware/` в VS Code
3. Build → Upload към ESP32
4. Свържи се по BLE и провери `status`
5. Свържи хардуера по [hardware/schematic.md](hardware/schematic.md)
6. Намери проводниците в колата по [docs/pinout.md](docs/pinout.md)

## Статус

- [x] Firmware — state machine, BLE, конфигурация
- [x] Хардуерна схема + BOM
- [ ] Намиране на AUTO и Unlock проводници в колата
- [ ] Прототип на breadboard
- [ ] Тест в кола
- [ ] Финален PCB

# Bluetooth конфигурация

## Свързване

1. Инсталирай **"Serial Bluetooth Terminal"** (Android) или **"BLE Terminal HM-10"** (iOS)
2. Включи контакта на колата (ESP32 се захранва от KL30 — включен е винаги)
3. В приложението: търси устройство **"Vectra Auto Lights"**
4. Свържи се → избери **Nordic UART Service**
5. Пиши команди в конзолата

---

## Команди

### `status`
Показва текущото състояние и всички настройки.

```
Състояние: DRL
Акумулатор: 14.12V

welcome.lights  = GABARI+FOG
welcome.time    = 30s
goodbye.lights  = GABARI
goodbye.time    = 45s
acc.lights      = GABARI
acc.enabled     = yes
```

### `set KEY=VALUE`
Сменя настройка. Записва се автоматично в паметта.

**Примери:**
```
set welcome.lights=GABARI+FOG+XENON
set welcome.time=20
set goodbye.lights=GABARI
set goodbye.time=60
set acc.lights=GABARI
set acc.enabled=0
set acc.enabled=1
```

**Стойности за светлини:**
- `GABARI` — само габарити (предни + задни)
- `FOG` — само предни мъгли
- `XENON` — само ксенон (⚠️ студен старт!)
- `GABARI+FOG` — комбинация
- `GABARI+FOG+XENON` — всичко
- `NONE` — нищо (изключен режим)

### `reset`
Връща всички настройки към стойностите по подразбиране.

### `help`
Показва кратка помощ.

---

## Настройки по подразбиране

| Настройка | Default |
|-----------|---------|
| welcome.lights | GABARI |
| welcome.time | 30s |
| goodbye.lights | GABARI |
| goodbye.time | 30s |
| acc.lights | GABARI |
| acc.enabled | yes |

---

## Бележка за ксенон в welcome/goodbye

D1S ксенонът има ограничен брой студени старта. Ако е включен в welcome lights, след края на таймера ще се изгаси, и след малко ще се запали отново при стартиране на двигателя — **два студени старта наведнъж**.

Изключение: ако двигателят запали по време на welcome таймера, ксенонът **не се изгася** — директно преминава в DRL режим.

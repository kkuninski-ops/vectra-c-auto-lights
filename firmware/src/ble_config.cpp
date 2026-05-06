#include "ble_config.h"
#include "config.h"
#include "inputs.h"
#include "state_machine.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

/* Nordic UART Service — поддържа се от повечето BLE terminal приложения */
#define NUS_SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_RX_UUID      "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_TX_UUID      "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

static BLEServer*         pServer  = nullptr;
static BLECharacteristic* pTxChar  = nullptr;
static bool               _connected = false;

/* ── Изпращане към телефона ─────────────────────────────────────────── */

static void ble_send(const String& msg) {
    if (!_connected || !pTxChar) return;
    /* BLE MTU обикновено е 20 байта — изпращаме на парчета */
    size_t len = msg.length();
    size_t pos = 0;
    while (pos < len) {
        size_t chunk = min((size_t)20, len - pos);
        pTxChar->setValue((uint8_t*)(msg.c_str() + pos), chunk);
        pTxChar->notify();
        delay(20);
        pos += chunk;
    }
    /* Нов ред като терминатор */
    pTxChar->setValue((uint8_t*)"\n", 1);
    pTxChar->notify();
}

/* ── Обработка на команди ───────────────────────────────────────────── */

static const char* HELP =
    "Команди:\n"
    "  status              — текущо състояние и конфиг\n"
    "  set KEY=VALUE       — смени настройка\n"
    "  reset               — върни към default\n"
    "\n"
    "Ключове:\n"
    "  welcome.lights  = GABARI / FOG / XENON (или комбинация с +)\n"
    "  welcome.time    = секунди (0-300)\n"
    "  goodbye.lights  = GABARI / FOG / XENON\n"
    "  goodbye.time    = секунди (0-300)\n"
    "  acc.lights      = GABARI / FOG / NONE\n"
    "  acc.enabled     = 0 / 1\n"
    "\n"
    "Пример: set welcome.lights=GABARI+FOG\n";

static void process_command(const String& raw) {
    String cmd = raw;
    cmd.trim();
    if (cmd.isEmpty()) return;

    if (cmd == "help" || cmd == "?") {
        ble_send(HELP);
        return;
    }

    if (cmd == "status") {
        String s = "Състояние: ";
        s += sm_state_name();
        s += "\nАкумулатор: ";
        s += String(inputs_vbat_mv() / 1000.0f, 2);
        s += "V\n\n";
        s += config_to_string();
        ble_send(s);
        return;
    }

    if (cmd == "reset") {
        config_reset_defaults();
        ble_send("OK: нулиране към default");
        return;
    }

    if (cmd.startsWith("set ")) {
        String rest = cmd.substring(4);
        rest.trim();
        int eq = rest.indexOf('=');
        if (eq < 0) { ble_send("ГРЕШКА: очаква се 'set KEY=VALUE'"); return; }
        String key = rest.substring(0, eq);
        String val = rest.substring(eq + 1);
        key.trim(); val.trim();
        key.toLowerCase();
        if (config_set(key, val))
            ble_send("OK: " + key + " = " + val);
        else
            ble_send("ГРЕШКА: непознат ключ '" + key + "'");
        return;
    }

    ble_send("ГРЕШКА: непозната команда. Пиши 'help' за помощ.");
}

/* ── BLE callbacks ──────────────────────────────────────────────────── */

class ServerCB : public BLEServerCallbacks {
    void onConnect(BLEServer*)    override { _connected = true;  }
    void onDisconnect(BLEServer*) override {
        _connected = false;
        BLEDevice::startAdvertising();
    }
};

class RxCB : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* c) override {
        process_command(String(c->getValue().c_str()));
    }
};

/* ── Public API ─────────────────────────────────────────────────────── */

void ble_init() {
    BLEDevice::init("Vectra Auto Lights");

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCB());

    BLEService* svc = pServer->createService(NUS_SERVICE_UUID);

    pTxChar = svc->createCharacteristic(NUS_TX_UUID, BLECharacteristic::PROPERTY_NOTIFY);
    pTxChar->addDescriptor(new BLE2902());

    BLECharacteristic* pRxChar = svc->createCharacteristic(
        NUS_RX_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    pRxChar->setCallbacks(new RxCB());

    svc->start();

    BLEAdvertising* adv = BLEDevice::getAdvertising();
    adv->addServiceUUID(NUS_SERVICE_UUID);
    adv->setScanResponse(true);
    BLEDevice::startAdvertising();
}

void ble_tick()      { /* BLE е event-driven — нищо не е нужно тук */ }
bool ble_connected() { return _connected; }

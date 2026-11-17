import network
import time
import dht
import machine
import urequests

# -----------------------------
# CONFIGURACION WIFI
# -----------------------------
SSID = "iPhone de Andres"
PASSWORD = "12345678"

# -----------------------------
# CONFIGURACION UBIDOTS
# -----------------------------
TOKEN = "BBUS-KtOwLoKmGORmggDtEaaCOUJrWOuPG3"
DEVICE_LABEL = "esp32_mina"

URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_LABEL
HEADERS = {
    "X-Auth-Token": TOKEN,
    "Content-Type": "application/json"
}

# -----------------------------
# ASIGNACIÓN DE PINES
# -----------------------------
# Sensor DHT11
sensor_clima = dht.DHT11(machine.Pin(4))

# Sensor de Gas MQ-2 (Lectura Analógica)
sensor_gas = machine.ADC(machine.Pin(34))
sensor_gas.atten(machine.ADC.ATTN_11DB) # Permite leer hasta 3.3V

# Actuadores de Alerta
buzzer = machine.Pin(25, machine.Pin.OUT)
led_rojo = machine.Pin(26, machine.Pin.OUT)   # LED_R: Peligro
led_verde = machine.Pin(27, machine.Pin.OUT)  # LED_A (Asumido como Verde): Seguro

# -----------------------------
# UMBRALES
# -----------------------------
UMBRAL_GAS = 3100 # Valor de lectura ADC desde el cual se considera peligroso (ajustar en pruebas)

def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    
    if not wifi.isconnected():
        print("Conectando a WiFi...")
        wifi.connect(SSID, PASSWORD)
        
        while not wifi.isconnected():
            print(".", end="")
            time.sleep(1)
            
    print("\nWiFi conectado")
    print("IP:", wifi.ifconfig()[0])
    return wifi

def enviar_ubidots(temp, hum, gas, estado):
    # Siempre empaqueta el nivel de gas y el estado de alerta
    datos = {
        "nivel_gas": gas,
        "estado_alerta": estado
    }
    
    # Solo agrega temperatura y humedad si el DHT11 funcionó correctamente en este ciclo
    if temp is not None:
        datos["temperatura"] = temp
        datos["humedad"] = hum

    try:
        respuesta = urequests.post(URL, json=datos, headers=HEADERS)
        print("Respuesta Ubidots:", respuesta.status_code)
        
        if respuesta.status_code in (200, 201):
            print("Datos enviados correctamente")
        else:
            print("Error enviando datos")
            print(respuesta.text)
            
        respuesta.close()
    except Exception as error:
        print("Error de conexion con Ubidots:", error)

# -----------------------------
# BUCLE PRINCIPAL
# -----------------------------
wifi = conectar_wifi()

# Estado inicial: apagar todo
led_rojo.value(0)
led_verde.value(0)
buzzer.value(0)

while True:
    if not wifi.isconnected():
        wifi = conectar_wifi()
        
    print("-----------------------------")
    
    # 1. Leer Sensor DHT11
    try:
        sensor_clima.measure()
        temperatura = sensor_clima.temperature()
        humedad = sensor_clima.humidity()
        print("Temperatura:", temperatura, "C")
        print("Humedad:", humedad, "%")
    except Exception as error:
        print("Error leyendo DHT11:", error)
        temperatura = None
        humedad = None

    # 2. Leer Sensor de Gas MQ-2
    nivel_gas = sensor_gas.read()
    print("Nivel de Gas (ADC):", nivel_gas)
    
    # 3. Lógica de Alertas y Semáforo
    if nivel_gas >= UMBRAL_GAS:
        print("¡PELIGRO! Nivel de gas alto. NO es seguro entrar.")
        led_rojo.value(1)
        buzzer.value(1)
        led_verde.value(0)
        estado_alerta = 1
    else:
        print("Ambiente SEGURO. Acceso permitido.")
        led_rojo.value(0)
        buzzer.value(0)
        led_verde.value(1)
        estado_alerta = 0

    # 4. Enviar a Ubidots (Ahora se ejecuta SIEMPRE)
    enviar_ubidots(temperatura, humedad, nivel_gas, estado_alerta)
        
    time.sleep(1)
import network
import time

# CONFIGURACIÓN WIFI
SSID = "iPhone de Andres"
PASSWORD = "12345678"

print("        INICIANDO ESP32")

wifi = network.WLAN(network.WLAN.IF_STA)

wifi.active(True)

print("Activando Wi-Fi...")

if not wifi.isconnected():
    
    print("Conectando a:", SSID)
    
    wifi.connect(SSID, PASSWORD)
    
    while not wifi.isconnected():
        
        print(".", end="")
        
        time.sleep(1)

print()
print("Wi-Fi conectado correctamente")

config = wifi.ifconfig()

print("        CONFIGURACIÓN DE RED")

print("IP:", config[0])
print("Máscara:", config[1])
print("Gateway:", config[2])
print("DNS:", config[3])

print("          ESP32 LISTA")


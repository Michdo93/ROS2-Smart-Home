"""Kapitel 18: ROS 2 und ZeroMQ im Vergleich – Latenz von Kamerabildern (640x480 RGB).

Ein Sender-Prozess schickt 300 Bilder mit 30 Hz, der Empfänger misst die Zeit vom Senden
bis zum Empfang. Beide laufen auf demselben Rechner – im Netz kommt die Übertragung dazu.

    ros2 run sh_kamera vergleich_zmq
"""
import multiprocessing as mp
import statistics
import struct
import time

import numpy as np

BILDER, HZ, GROESSE = 300, 30.0, (480, 640, 3)
PROZESSE = mp.get_context("spawn")                  # frischer Python-Prozess je Sender


def bild(i):
    b = np.zeros(GROESSE, np.uint8)
    b[..., 0] = i % 256
    return b.tobytes()


# ------------------------------------------------------------------ ZeroMQ
def zmq_sender():
    import zmq
    s = zmq.Context().socket(zmq.PUB)
    s.bind("tcp://127.0.0.1:5590")
    time.sleep(1.0)                                   # "slow joiner" abwarten
    for i in range(BILDER):
        s.send_multipart([struct.pack("d", time.time()), bild(i)])
        time.sleep(1 / HZ)


def zmq_messen():
    import zmq
    s = zmq.Context().socket(zmq.SUB)
    s.connect("tcp://127.0.0.1:5590")
    s.setsockopt(zmq.SUBSCRIBE, b"")
    s.setsockopt(zmq.RCVTIMEO, 3000)
    p = PROZESSE.Process(target=zmq_sender)
    p.start()
    werte = []
    try:
        while len(werte) < BILDER:
            stempel, _ = s.recv_multipart()
            werte.append((time.time() - struct.unpack("d", stempel)[0]) * 1000)
    except zmq.Again:
        pass
    p.join()
    return werte


# ------------------------------------------------------------------ ROS 2
def ros_sender(zuverlaessig):
    import rclpy
    from rclpy.qos import QoSProfile, qos_profile_sensor_data
    from sensor_msgs.msg import Image
    rclpy.init()
    n = rclpy.create_node("vergleich_sender")
    qos = QoSProfile(depth=2) if zuverlaessig else qos_profile_sensor_data
    pub = n.create_publisher(Image, "/vergleich/bild", qos)
    while pub.get_subscription_count() == 0:
        time.sleep(0.1)
    time.sleep(0.5)
    for i in range(BILDER):
        m = Image(height=480, width=640, encoding="rgb8", step=1920, data=bild(i))
        t = time.time()
        m.header.stamp.sec, m.header.stamp.nanosec = int(t), int((t % 1) * 1e9)
        pub.publish(m)
        time.sleep(1 / HZ)
    time.sleep(0.5)
    rclpy.shutdown()


def ros_messen(zuverlaessig):
    import rclpy
    from rclpy.qos import QoSProfile, qos_profile_sensor_data
    from sensor_msgs.msg import Image
    p = PROZESSE.Process(target=ros_sender, args=(zuverlaessig,))
    p.start()
    rclpy.init()
    n = rclpy.create_node("vergleich_empfaenger")
    werte = []
    qos = QoSProfile(depth=2) if zuverlaessig else qos_profile_sensor_data
    n.create_subscription(Image, "/vergleich/bild", lambda m: werte.append(
        (time.time() - m.header.stamp.sec - m.header.stamp.nanosec / 1e9) * 1000), qos)
    ende = time.time() + BILDER / HZ + 10
    while len(werte) < BILDER and time.time() < ende and p.is_alive():
        rclpy.spin_once(n, timeout_sec=0.1)
    p.join()
    rclpy.shutdown()
    return werte


def zeile(name, werte):
    if not werte:
        return f"{name:<26} keine Bilder empfangen"
    q = statistics.quantiles(werte, n=100)
    median = statistics.median(werte)
    return (f"{name:<26} {len(werte):4d}/{BILDER}  Median {median:6.2f} ms"
            f"  p95 {q[94]:6.2f} ms  max {max(werte):6.2f} ms")


def main():
    mb = np.prod(GROESSE) * HZ / 1e6
    print(f"{BILDER} Bilder 640x480 RGB mit {HZ:.0f} Hz ({mb:.1f} MB/s), gleicher Rechner")
    print(zeile("ZeroMQ PUB/SUB (TCP)", zmq_messen()))
    print(zeile("ROS 2 reliable", ros_messen(True)))
    print(zeile("ROS 2 best effort", ros_messen(False)))


if __name__ == "__main__":
    main()

"""Kapitel 2: ROS 2 meldet einen Zustand und schickt einen Befehl ins Smart Home.

Zustand: die Position der Schildkröte, einmal pro Sekunde als geometry_msgs/Point.
Befehl:  kommt die Schildkröte dem Rand näher als 1 m, soll das Flurlicht angehen
         ("ON"); ist sie wieder mehr als 1,5 m entfernt, geht es aus ("OFF").
"""
import rclpy
from geometry_msgs.msg import Point
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String
from turtlesim.msg import Pose

RAND = 11.09    # turtlesim-Fenster: 0 ... 11,09 m


def abstand_zum_rand(x, y):
    return min(x, y, RAND - x, RAND - y)


class SchildkroeteMelder(Node):
    def __init__(self):
        super().__init__("schildkroete_melder")
        self.pose = None
        self.licht = None
        self.pub_position = self.create_publisher(Point, "/schildkroete/position", 10)
        self.pub_befehl = self.create_publisher(String, "/haus/flurlicht/befehl", 10)
        self.create_subscription(Pose, "/turtle1/pose", self.neue_pose, 10)
        self.create_timer(1.0, self.melden)

    def neue_pose(self, pose):
        self.pose = pose                      # 62-mal pro Sekunde – nur merken

    def melden(self):
        if self.pose is None:
            return
        x, y = round(self.pose.x, 2), round(self.pose.y, 2)
        self.pub_position.publish(Point(x=x, y=y))
        abstand = abstand_zum_rand(x, y)
        licht = "ON" if abstand < 1.0 else "OFF" if abstand > 1.5 else self.licht
        if licht is not None and licht != self.licht:
            self.licht = licht
            self.pub_befehl.publish(String(data=licht))
            self.get_logger().info(
                f"x={x} y={y}, {abstand:.2f} m vom Rand -> Flurlicht {licht}")


def main(args=None):
    rclpy.init(args=args)
    knoten = SchildkroeteMelder()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()

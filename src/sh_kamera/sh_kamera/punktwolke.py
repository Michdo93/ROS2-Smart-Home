"""Kapitel 13: Punktwolke lesen – wo ist der nächste Punkt vor der Kamera?

    ros2 run sh_kamera punktwolke
"""
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class Punktwolke(Node):
    def __init__(self):
        super().__init__("punktwolke")
        thema = self.declare_parameter("wolke", "/kinect_v1/depth/points").value
        self.create_subscription(PointCloud2, thema, self.wolke, 2)
        self.zaehler = 0

    def wolke(self, m):
        self.zaehler += 1
        if self.zaehler % 10 != 1:
            return
        p = point_cloud2.read_points_numpy(m, field_names=("x", "y", "z"), skip_nans=True)
        if len(p) == 0:
            return
        naechster = p[np.argmin(p[:, 2])]          # optischer Rahmen: z zeigt nach vorn
        felder = ",".join(f.name for f in m.fields)
        self.get_logger().info(
            f"{len(p)} Punkte ({felder}) in {m.header.frame_id}, nächster: "
            f"x={naechster[0]:+.2f} y={naechster[1]:+.2f} z={naechster[2]:.2f} m")


def main(args=None):
    rclpy.init(args=args)
    knoten = Punktwolke()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()

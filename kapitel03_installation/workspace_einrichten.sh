#!/usr/bin/env bash
# Kapitel 3: Workspace mit allen Paketen des Buchs anlegen und bauen
set -euo pipefail
WS=${1:-$HOME/ros2_ws}
mkdir -p "$WS/src" && cd "$WS/src"
for repo in ROS2-Smart-Home ros2_openhab_ws ROS2-Kinect-v1-Xbox-360 ROS2-Kinect-v2-Xbox-One; do
  [ -d "$repo" ] || git clone "https://github.com/Michdo93/$repo.git"
done
pip install --break-system-packages python-openhab-rest-client opencv-python-headless pyzmq
cd "$WS"
source /opt/ros/*/setup.bash
rosdep update || true
rosdep install --from-paths src --ignore-src -y -r || true   # fehlende Pakete nachinstallieren
colcon build --symlink-install
echo "Fertig: source $WS/install/setup.bash"

#!/usr/bin/env bash
# Kapitel 4: ROS 2 aus den offiziellen Paketquellen installieren
#   Ubuntu 26.04 -> Lyrical Luth, Ubuntu 24.04 -> Jazzy Jalisco (auch Raspberry Pi 4/5, 64 Bit)
#   ./ros2_installieren.sh            # ros-<distro>-ros-base (ohne Oberflächen, für den Pi)
#   ./ros2_installieren.sh desktop    # mit RViz, rqt und turtlesim
set -euo pipefail
. /etc/os-release
case "$VERSION_CODENAME" in
  resolute) DISTRO=lyrical ;;
  noble)    DISTRO=jazzy ;;
  *) echo "Ubuntu $VERSION_ID wird nicht unterstützt (26.04 oder 24.04)"; exit 1 ;;
esac
UMFANG=${1:-ros-base}
echo "Installiere ROS 2 $DISTRO ($UMFANG) auf Ubuntu $VERSION_ID ($(uname -m))"

sudo apt-get update
sudo apt-get install -y locales software-properties-common curl
sudo locale-gen de_DE.UTF-8 en_US.UTF-8
sudo add-apt-repository -y universe

# Paketquelle über das Paket ros2-apt-source (enthält Schlüssel und Quelle)
VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
  | grep -F '"tag_name"' | cut -d'"' -f4)
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${VERSION}/ros2-apt-source_${VERSION}.${VERSION_CODENAME}_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt-get update
sudo apt-get install -y "ros-${DISTRO}-${UMFANG}" ros-dev-tools python3-pip \
  "ros-${DISTRO}-tf2-ros" "ros-${DISTRO}-diagnostic-msgs"
[ "$UMFANG" = desktop ] && sudo apt-get install -y "ros-${DISTRO}-turtlesim" \
  "ros-${DISTRO}-rqt-image-view"

grep -q "/opt/ros/${DISTRO}/setup.bash" ~/.bashrc || cat >> ~/.bashrc <<RC

# ROS 2 (Smart Home & ROS2, Kapitel 4)
source /opt/ros/${DISTRO}/setup.bash
export ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-7}
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
[ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash
RC
echo "Fertig. Neues Terminal öffnen und prüfen: ros2 doctor --report | head"

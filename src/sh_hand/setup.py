from glob import glob

from setuptools import find_packages, setup

paket = "sh_hand"

setup(
    name=paket,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + paket]),
        ("share/" + paket, ["package.xml"]),
        ("share/" + paket + "/launch", glob("launch/*.launch.py")),
        ("share/" + paket + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Michael Christian Dörflinger",
    maintainer_email="michdo93@users.noreply.github.com",
    description="Kapitel 19: Hand erkannt – Kinect, ROS 2, openHAB oder Home Assistant",
    license="MIT",
    tests_require=["pytest"],
    entry_points={"console_scripts": ["hand_detektor = sh_hand.hand_detektor:main"]},
)

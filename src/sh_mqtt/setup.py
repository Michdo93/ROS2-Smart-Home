from glob import glob

from setuptools import setup

paket = "sh_mqtt"
setup(
    name=paket,
    version="1.0.0",
    packages=[paket],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{paket}"]),
        (f"share/{paket}", ["package.xml"]),
        (f"share/{paket}/config", glob("config/*.yaml")),
        (f"share/{paket}/launch", glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Michael Christian Dörflinger",
    maintainer_email="michdo93@users.noreply.github.com",
    description="ROS 2 und Smart Home über MQTT",
    license="MIT",
    entry_points={
        "console_scripts": [
            "temperatur_farbe = sh_mqtt.temperatur_farbe:main",
            "schildkroete_melder = sh_mqtt.schildkroete_melder:main",
        ],
    },
)

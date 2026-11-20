from glob import glob

from setuptools import find_packages, setup

paket = "sh_szenarien"

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
    description="Kapitel 13 und 14: Szenarien, Roboter und Haus mit der openHAB-Brücke",
    license="MIT",
    entry_points={"console_scripts": [
        "turtle_kontrollgang = sh_szenarien.turtle_kontrollgang:main",
        "openhab_kontrollgang = sh_szenarien.openhab_kontrollgang:main",
        "haus_roboter = sh_szenarien.haus_roboter:main",
    ]},
)

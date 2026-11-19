from glob import glob

from setuptools import find_packages, setup

paket = "sh_kamera"

setup(
    name=paket,
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + paket]),
        ("share/" + paket, ["package.xml"]),
        ("share/" + paket + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Michael Christian Dörflinger",
    maintainer_email="michdo93@users.noreply.github.com",
    description="Kapitel 13 und 16: Kamerabilder messen, komprimieren, teilen",
    license="MIT",
    entry_points={"console_scripts": [
        "bandbreite = sh_kamera.bandbreite:main",
        "kompressor = sh_kamera.kompressor:main",
        "bewegung = sh_kamera.bewegung:main",
        "vergleich_zmq = sh_kamera.vergleich_zmq:main",
    ]},
)

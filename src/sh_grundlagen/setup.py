from glob import glob

from setuptools import find_packages, setup

paket = "sh_grundlagen"
knoten = ["raumklima_sender", "raumklima_empfaenger", "lichtszene_server",
          "lichtszene_client", "kontrollgang_server", "kontrollgang_client", "qos_demo"]

setup(
    name=paket,
    version="1.0.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + paket]),
        ("share/" + paket, ["package.xml"]),
        ("share/" + paket + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Michael Christian Dörflinger",
    maintainer_email="michdo93@users.noreply.github.com",
    description="Kapitel 5 bis 7: Knoten, Topics, Services, Actions, QoS, Launch",
    license="MIT",
    entry_points={"console_scripts": [f"{k} = {paket}.{k}:main" for k in knoten]},
)

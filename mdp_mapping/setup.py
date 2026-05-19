from setuptools import setup
from glob import glob
import os

package_name = "mdp_mapping"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "maps"), glob("maps/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Francis Zheng",
    maintainer_email="Z.Zheng-13@student.tudelft.nl",
    description="Mapping package for MIRTE greenhouse robot using slam_toolbox.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "mapping_manager_node = mdp_mapping.mapping_manager_node:main",
        ],
    },
)
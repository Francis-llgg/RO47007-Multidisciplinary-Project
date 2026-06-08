from glob import glob
import os

from setuptools import setup


package_name = "mdp_navigation"


setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        (
            os.path.join("share", "ament_index", "resource_index", "packages"),
            ["resource/" + package_name],
        ),
        (os.path.join("share", package_name), ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Francis Zheng",
    maintainer_email="Z.Zheng-13@student.tudelft.nl",
    description="Navigation configuration package for MIRTE greenhouse robot.",
    license="MIT",
    tests_require=["pytest"],
)
from setuptools import find_packages, setup

package_name = 'mirte_launch'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
		('share/' + package_name + '/launch', ['launch/mirte_launch.py']),
        ('share/' + package_name + '/config', ['config/nav2_params.yaml']),
        ('share/' + package_name + '/maps', ['maps/map.yaml', 'maps/map.pgm']),
		('share/' + package_name + '/worlds', ['../greenhouse_simulation/worlds/greenhouse.world']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bram',
    maintainer_email='bakalkman@tudelft.nl',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)

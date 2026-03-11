from setuptools import find_packages, setup

package_name = 'smart_classroom_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/classroom_demo.launch.py']),
        ('share/' + package_name + '/config', ['config/classroom_demo.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='reeve',
    maintainer_email='reeve@todo.todo',
    description='ROS 2 Humble smart classroom notice and attendance demo',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'teacher_node = smart_classroom_demo.teacher_node:main',
            'student_node = smart_classroom_demo.student_node:main',
            'office_node = smart_classroom_demo.office_node:main',
            'dashboard_node = smart_classroom_demo.dashboard_node:main',
        ],
    },
)

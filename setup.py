from setuptools import setup


setup(
    name='cldfbench_multitree',
    py_modules=['cldfbench_multitree'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'multitree=cldfbench_multitree:Dataset',
        ],
        'cldfbench.commands': [
            'multitree=multitree_commands',
        ]
    },
    install_requires=[
        'python-nexus',
        'lxml',
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

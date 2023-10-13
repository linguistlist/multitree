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
        'commonnexus>=1.7',
        'unidecode',
        'lxml',
        'cldfbench',
        'commonnexus',
        'pycldf',
        'clldutils',
        'newick',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)

from setuptools import setup

setup(
    name='rofi-generic',
    version='0.1.0',
    description='Simple text picker using rofi',
    author='kamaradclimber',
    author_email='grego_rofigeneric@familleseux.net',
    url='https://github.com/kamaradclimber/rofi-generic',
    keywords='rofi picker rofimoji jira',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],

    packages=['picker'],
    package_data={
        'picker': ['data/*.csv']
    },
    entry_points={
        'console_scripts': [
            'rofi-generic = picker.RofiGeneric:main'
        ]
    },
    install_requires=[
        'pyxdg==0.26',
        'ConfigArgParse>0.15,<2.0.0'
    ]
)

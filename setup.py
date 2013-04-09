from setuptools import setup
from ahc import VERSION


setup(
    name='ahc',
    version=".".join(map(str, VERSION)),
    description='Package with extensions for Developers on '
                'Python(+Django), Ruby(+RoR) and PHP.',
    keywords="console utils developers",
    long_description=open('README').read(),
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='http://github.com/gotlium/ahc',
    license='GPL-2',
    packages=['ahc'],
    package_data={'ahc': [
        'templates/*',
        'configs.cfg',
        'libraries/*',
        'modules/*',
        'tests/*',
    ]},
    include_package_data=True,
    install_requires=[
        'setuptools', 'MySQL-python', 'django',
        'flup', 'pycurl', 'grab', 'paramiko',
        'xmpppy', 'virtualenv'],
    zip_safe=False,
    namespace_packages=['ahc'],
    entry_points={
        'console_scripts': ['ahc = ahc.ahc:run']
    },
    classifiers=[
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
)

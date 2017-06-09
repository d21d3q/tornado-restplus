from setuptools import setup


tests_require = ['pytest', 'pytest-cov']
setup_requires = ['pytest-runner']
install_requires = ['tornado', 'apispec']

setup(
    name='tornado-restplus',
    version='0.0.1dev0',
    url='https://github.com/d21d3q/tornado-restplus',
    author='Zdzislaw Krajewski',
    author_email='zdzislaw.krajewski@protonmail.ch',
    packages=['tornado_restplus'],
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    license='MIT',
    long_description=open('README.md').read(),
)

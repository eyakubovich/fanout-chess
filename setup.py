from setuptools import setup

setup(name='FanoutChess',
      version='1.0',
      description='Chess using Fanout.io',
      author='Eugene Yakubovich',
      author_email='example@example.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['bottle', 'requests', 'PyJWT', 'redis']
     )

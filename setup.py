import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

from setuptools.command.install import install as _install
import inspect


build_dir = ''


def _post_install(dir):
    global build_dir
    print build_dir
    subprocess.check_call(['make', 'install', ], cwd=build_dir)


class install(_install):
    def run(self):
        print 'VV:'
        print self._called_from_setup(inspect.currentframe())
        self.do_egg_install()
        #super(_install,self).run()
        self.execute(_post_install, (self.install_lib,),
                     msg="Running cmake install task")


class CMakeExtension(Extension):

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):

    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,]
        if os.environ.get('CMAKE_INSTALL_PREFIX') is not None:
            cmake_args.append('-DCMAKE_INSTALL_PREFIX='+os.environ['CMAKE_INSTALL_PREFIX'])

        # XXX: if pdb is set, use a debug build
        cmdline_args = self.distribution.script_args
        cmdline_args = [arg.strip('--') for arg in cmdline_args]
        do_debug = self.debug
        if 'pdb' in cmdline_args and ('test' in cmdline_args or 'nosetests' in cmdline_args):
            do_debug = True

        cfg = 'Debug' if do_debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2 ** 32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        global build_dir
        build_dir = self.build_temp 


def get_version_from_cmake_file(cmake_file):
    with open(cmake_file,'r') as f:
        lines = [ l.strip() for l in f.readlines() ]
    major_line = filter(lambda l: l.find('set(PROJECT_VERSION_MAJOR') != -1,lines)[0]
    minor_line = filter(lambda l: l.find('set(PROJECT_VERSION_MINOR') != -1,lines)[0]
    patch_line = filter(lambda l: l.find('set(PROJECT_VERSION_PATCH') != -1,lines)[0]
    def get_num_from_line(line):
        return (line.split(' ')[-1].split(')')[0])
    version = '.'.join(map(get_num_from_line,[major_line,minor_line,patch_line]))
    return version


__version__ = get_version_from_cmake_file('CMakeLists.txt')


setup(
    name='cndarray',
    version=__version__,
    author='Matt Gara',
    author_email='gara.matt@gmail.com',
    description='A simple interface to use numpy.ndarray in C++ or C code, allowing python to hold ownership at all times.',
    long_description='',
    ext_modules=[CMakeExtension('cndarray')],
    cmdclass=dict(build_ext=CMakeBuild,install=install),
    #cmdclass=dict(build_ext=CMakeBuild),
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=['numpy',],
    packages=['cndarray'],
    zip_safe=False,
)

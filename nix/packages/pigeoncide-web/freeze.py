"""
Freezes Pigeoncide and links it with CPython and Panda3D, all built for
Emscripten, into a single pigeoncide.js/pigeoncide.wasm pair.

Run with a host Python of the same minor version as the target, so the
frozen bytecode matches. The host needs panda3d.core (any desktop build)
and must import the direct package of the web Panda3D build, whose
FreezeTool this uses. Adapted from rdb's freezify.py for the Panda3D
WebGL port.

Usage: freeze.py SRC_DIR ASSET_DIR PYTHON_PREFIX PANDA_BUILT ODE_PREFIX OUT_DIR
"""

import os
import sys

from direct.dist import FreezeTool

SRC_DIR, ASSET_DIR, PY_PREFIX, PANDA_BUILT, ODE_PREFIX, OUT_DIR = \
    map(os.path.abspath, sys.argv[1:7])

PY_VERSION = '3.12'
PY_INCLUDE_DIR = f'{PY_PREFIX}/include/python{PY_VERSION}'
PY_LIB_DIR = f'{PY_PREFIX}/lib'
PY_STDLIB_DIR = f'{PY_LIB_DIR}/python{PY_VERSION}'
PY_LIBS = ['libpython3.12.a', 'libmpdec.a', 'libexpat.a', 'libHacl_Hash_SHA2.a']

# Extension modules of the panda3d package, and the native libraries they
# need. The game uses ODE for physics and panda3d.physics for particles.
PANDA_MODULES = ['core', 'direct', 'ode', 'physics']
PANDA_LIBS = ['libpanda', 'libpandaexpress', 'libp3dtool', 'libp3dtoolconfig',
              'libp3webgldisplay', 'libp3direct', 'libp3openal_audio',
              'libpandaode', 'libpandaphysics']

INITIAL_HEAP = 256 * 1024 * 1024
STACK_SIZE = 4 * 1024 * 1024

# Where the assets appear in the in-memory file system of the page; must
# match WEB_ROOT in src/core/paths.py.
WEB_ROOT = '/pigeoncide'


def link_flags():
    flags = [os.path.join(PY_LIB_DIR, lib) for lib in PY_LIBS
             if os.path.isfile(os.path.join(PY_LIB_DIR, lib))]
    for mod in PANDA_MODULES:
        flags.append(f'{PANDA_BUILT}/lib/libpy.panda3d.{mod}.cpython-312-wasm32-emscripten.a')
    flags += [f'{PANDA_BUILT}/lib/{lib}.a' for lib in PANDA_LIBS]
    flags.append(f'{ODE_PREFIX}/lib/libode.a')
    flags += ['-sUSE_ZLIB=1', '-sUSE_VORBIS=1', '-sUSE_FREETYPE=1',
              '-sUSE_HARFBUZZ=1', '-sUSE_BZIP2=1', '-sUSE_SQLITE3=1',
              '-sDISABLE_EXCEPTION_THROWING=0', '-sMAX_WEBGL_VERSION=2',
              '-sNO_EXIT_RUNTIME=1', '-sALLOW_MEMORY_GROWTH=1',
              f'-sINITIAL_HEAP={INITIAL_HEAP}', f'-sSTACK_SIZE={STACK_SIZE}',
              '--preload-file', f'{ASSET_DIR}@{WEB_ROOT}']
    return ' '.join(flags)


class EmscriptenEnvironment:
    platform = 'emscripten'
    Python = None
    PythonIPath = PY_INCLUDE_DIR
    PythonVersion = PY_VERSION
    suffix64 = ''
    dllext = ''
    arch = ''

    def compileExe(self, filename, basename, extraLink=[]):
        run(f'emcc -O3 -fno-exceptions -fno-rtti -c -o {basename}.o {filename} '
            f'-I{PY_INCLUDE_DIR} -I{PANDA_BUILT}/include')
        run(f'em++ -O3 -fno-exceptions -fno-rtti -o {basename}.js {basename}.o '
            f'{link_flags()} ' + ' '.join(extraLink))

    def compileDll(self, filename, basename, extraLink=[]):
        raise NotImplementedError('everything is linked statically')


def run(cmd):
    print(cmd, file=sys.stderr)
    if os.system(cmd) != 0:
        sys.exit(f'command failed: {cmd}')


FROZEN_MAIN = """
#include "Python.h"
#include <emscripten.h>

extern PyObject *PyInit_core();
extern PyObject *PyInit_direct();
extern PyObject *PyInit_ode();
extern PyObject *PyInit_physics();

extern void init_libOpenALAudio();
extern void init_libpnmimagetypes();
extern void init_libwebgldisplay();

extern void task_manager_poll();

static void add_panda_module(PyObject *package, PyObject *sys_modules,
                             const char *name, PyObject *module) {
  char qualified[64];
  snprintf(qualified, sizeof(qualified), "panda3d.%s", name);
  PyDict_SetItemString(PyModule_GetDict(package), name, module);
  PyDict_SetItemString(sys_modules, qualified, module);
}

int
Py_FrozenMain(int argc, char **argv)
{
    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.pathconfig_warnings = 0;
    config.use_environment = 0;
    config.write_bytecode = 0;
    config.site_import = 0;
    config.user_site_directory = 0;
    config.buffered_stdio = 0;

    PyStatus status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        return 1;
    }
    PyConfig_Clear(&config);

    PyObject *panda3d = PyImport_AddModule("panda3d");
    PyModule_AddStringConstant(panda3d, "__package__", "panda3d");
    PyModule_AddObject(panda3d, "__path__", PyList_New(0));

    PyObject *sys_modules = PySys_GetObject("modules");
    add_panda_module(panda3d, sys_modules, "core", PyInit_core());
    add_panda_module(panda3d, sys_modules, "direct", PyInit_direct());
    add_panda_module(panda3d, sys_modules, "ode", PyInit_ode());
    add_panda_module(panda3d, sys_modules, "physics", PyInit_physics());

    init_libOpenALAudio();
    init_libpnmimagetypes();
    init_libwebgldisplay();

    emscripten_set_main_loop(&task_manager_poll, 0, 0);

    if (PyImport_ImportFrozenModule("__main__") < 0) {
        PyErr_Print();
        return 1;
    }
    return 0;
}
"""

# Modules come only from the game, the Panda3D build and the target's
# standard library, never from the host Python running this script.
freezer = FreezeTool.Freezer(platform='emscripten_wasm32',
                             path=[SRC_DIR, PANDA_BUILT, PY_STDLIB_DIR])
freezer.frozenMainCode = FROZEN_MAIN
freezer.cenv = EmscriptenEnvironment()
for mod in ['doctest', 'difflib', 'panda3d', 'psyco', 'unittest', 'test',
            'tkinter', 'pydoc']:
    freezer.excludeModule(mod)
freezer.addModule('__main__', filename=os.path.join(SRC_DIR, 'main.py'))
# Imported inside ShowBase.enableParticles, which the module finder misses.
freezer.addModule('direct.showbase.PhysicsManagerGlobal')
freezer.addModule('direct.particles.*')
freezer.done(addStartupModules=True)

os.makedirs(OUT_DIR, exist_ok=True)
os.chdir(OUT_DIR)
freezer.generateCode('pigeoncide', compileToExe=True)

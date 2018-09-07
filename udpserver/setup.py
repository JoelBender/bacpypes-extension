from setuptools import setup, Extension

setup(
    name='udpserver',
    version='1.0',
    description='Sample Extension',
    ext_modules=[
        Extension(
            'custom',
            sources=['custom.c'],
            py_limited_api=True,
        )
    ],
)

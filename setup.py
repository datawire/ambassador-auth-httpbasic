import versioneer

from setuptools import setup, find_packages

setup(
    name="ambassador-auth-httpbasic",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "bcrypt",
        "flask",
        "gunicorn",
        "pyyaml"
    ],
    author="datawire.io",
    author_email="dev@datawire.io",
    url="https://github.com/datawire/ambassador-auth-httpbasic",
    download_url="https://github.com/datawire/ambassador-auth-httpbasic/tarball/{}".format(versioneer.get_version()),
    keywords=[
        "authentication",
        "getambassador.io",
        "kubernetes",
        "microservices"
    ],
    classifiers=[],
)

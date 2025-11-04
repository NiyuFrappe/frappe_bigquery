from setuptools import setup, find_packages

try:
    with open("requirements.txt") as f:
        install_requires = [l.strip() for l in f if l.strip() and not l.startswith("#")]
except FileNotFoundError:
    install_requires = []

setup(
    name="frappe_bigquery",
    version="0.0.1",
    description="BigQuery connector for Frappe/ERPNext",
    author="Niyu Labs",
    author_email="info@niyulabs.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    python_requires=">=3.10",
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ['responder', 'graphql-core==2.2.1', 'graphene==2.1.8', 'transformers[tf-cpu]==3.0.2', 'rake_nltk', 'nltk','sqlalchemy','sentence_transformers==0.3.0']

setuptools.setup(
    name="tableqa-abhijithneilabraham", # Replace with your own username
    version="0.0.1",
    author="Abhijith Neil Abraham, Fariz Rahman",
    author_email="abhijithneilabrahampk@gmail.com,farizrahman4u@gmail.com",
    description="Tool for querying natural language on tabular data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GNU GPL v2',
    url="https://github.com/abhijithneilabraham/tableQA",
    install_requires=install_requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
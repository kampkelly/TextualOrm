from setuptools import setup, find_packages

setup(
    name='textual_orm',
    version='0.1.2',
    packages=find_packages(),
    license='MIT',
    description='SQL Generator and Query Result Retriever',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'asyncpg==0.29.0',
        'redis[hiredis]==5.0.8',
        'langchain==0.2.12',
        'langchain-huggingface==0.0.3',
        'transformers==4.44.0',
        'langchain_community==0.2.11',
        'peft==0.12.0',
        'torch==2.4.0',
        'langchain-openai==0.1.21'
    ],
    python_requires='>=3.12',
    url='https://github.com/kampkelly/TextualOrm',
    author='Oghenerunor Adjekpiyede',
    author_email='kampkellykeys@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
    ],
)

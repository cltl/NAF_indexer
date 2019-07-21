# NAF indexer

The goal of this repository is to index NAF files such that we
can query for all sentences of a certain lemma and pos combination in a certain language.

### Prerequisites

Python 3.6 was used to create this project. It might work with older versions of Python.

### Installing


#### Python modules

A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

## How to use
Perform the following call for more information about usage
```
python represent_naf.py -h
```

Please check `how_to_use.py` for how to work with the output format.
    
## Authors
* **Marten Postma** (m.c.postma@vu.nl)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details

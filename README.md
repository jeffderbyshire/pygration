# Enstore Tape Migration Helper (Pygration)

This Repository is a Python collection of scripts used to help manage Enstore Tape Migration logs.
The main script is run with a few command line arguments.  

## Getting Started

* Setup Python 3.7 environment.
* Clone this repository
* Edit config/config.conf
* Run python setup.py
* Run python pygration check|process|logs [errors|no-errors|all]|status

### Prerequisites

* Python >= 3.7
* sqlite3
* python modules: sh, tqdm, click, sqlalchemy
* Enstore http://www-ccf.fnal.gov/enstore/

## Deployment

To continuously check for new logs during migration process add a cronjob.

```
Add cronjob to run /path/to/files/migrate_helper_scripts/check_logs.sh
```

## Versioning

We use [SemVer](http://semver.org/) for versions. For the versions available, see the [tags on this repository](https://github.com/jeffderbyshire/pygration/tags). 

## Authors

* **Jeff Derbyshire** - *Initial work* - [jeffderbyshire](https://github.com/jeffderbyshire)

## License

This project is licensed under the GNU/GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Fermilab](http://fnal.gov)


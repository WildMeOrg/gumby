#!/usr/bin/env python
from setuptools import setup


NAME = 'Gumby'
MAINTAINER = 'Wild Me, non-profit'
MAINTAINER_EMAIL = 'dev@wildme.org'
DESCRIPTION = 'Codex - Search Index'
LONG_DESCRIPTION = DESCRIPTION
KEYWORDS = ['wild me', 'hoston', 'wildbook']
URL = 'https://github.com/WildMeOrg/gumby'
DOWNLOAD_URL = ''
LICENSE = 'Apache License 2.0'
AUTHOR = MAINTAINER
AUTHOR_EMAIL = MAINTAINER_EMAIL
MAJOR = 0
MINOR = 1
MICRO = 0
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)
PACKAGES = ['gumby']
ENTRY_POINTS = {
    'pytest11': ["gumby = gumby.pytest"],
}


def parse_requirements(fname='requirements.txt', with_version=True):
    """
    Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        with_version (bool, default=True): if true include version specs

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
        python -c "import setup; print(chr(10).join(setup.parse_requirements(with_version=True)))"
    """
    import re
    import sys
    from os.path import exists

    require_fpath = fname

    def parse_line(line):
        """
        Parse information from a line in a requirements text file
        """
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip, rest.split(';'))
                        info['platform_deps'] = platform_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get('platform_deps')
                    if platform_deps is not None:
                        parts.append(';' + platform_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


def do_setup():
    # Define requirements
    requirements = parse_requirements('requirements.txt')
    # Define optional requirements (e.g. `pip install ".[testing]"`)
    optional_requirements = {}

    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        packages=PACKAGES,
        install_requires=requirements,
        extras_require=optional_requirements,
        entry_points=ENTRY_POINTS,
        package_data={
            'gumby': ['testing-data/*.json'],
        },
        include_package_data=True,
    )


if __name__ == '__main__':
    do_setup()

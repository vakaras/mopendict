PACKAGES=mopendict

test:
	bin/test $(PACKAGES) \
		--with-coverage --cover-package="$(PACKAGES)" \
		--cover-erase --cover-html --cover-html-dir=var/coverage

show-coverage: test
	xdg-open var/coverage/index.html

# Check code quality.
check:
	bin/pylint --rcfile .pylintrc $(PACKAGES) > var/pylint.html

show-check:
	xdg-open var/pylint.html

# Creating environment.

bootstrap.py:
	wget http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py

bin/buildout: bootstrap.py
	python bootstrap.py

buildout: bin/buildout
	bin/buildout -v

# Create source distribution.
source_dist:
	python setup.py sdist

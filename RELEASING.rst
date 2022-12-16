#. Verify tests are passing (``python setup.py test``)
#. Verify test code coverage is above minimum (``python code_coverage.py``)
#. Bump the version number in boyermoore/__init__.py
#. Bump the version number in sphinx_docs/source/conf.py
#. Build HTML API docs (``cd sphinx_docs && make html && cp -r build/html ../docs``)
#. Build PDF API docs (you may want to first delete/comment out the TOC at
   the top of README.rst ) (``make latexpdf``)
#. Rename PDF API docs to ``boyermoore_x.x.x_documentation.pdf``
#. Ensure TOC in README.rst is restored/uncommented
#. Make a new commit, adding all changed files (don't forget ``docs``)
#. Tag the new commit with the next version and push (``git tag vx.x.x && git push origin master --tags``)
#. Build the wheel file (``python setup.py bdist_wheel``)
#. Make a new release on github, against tag ``vx.x.x``, release name should match the tag name.
   Make sure to add the PDF API docs file and the wheel file.
#. Push wheel file to pypi (``python -m twine upload dist/boyermoore-x.x.x-py3-none-any.whl``)

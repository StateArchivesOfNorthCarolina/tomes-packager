# Ideas for Future Work

- Given how long it can take to build the METS manifest file with file checksums, consider adding logging statements that address how many files have been processed and how many more are left to process, i.e. "1 of 500 files have been processed ...".
- Clarify what is meant by "account_id" in the graphics.
- Add documentation on how to re-package contents (data already in the correct folder structure), e.g.:
	- `python3 packager.py foo ../tests/sample_files/ ../tests/sample_files/`
	- In other words, pass the parent folder of the containing AIP directory `foo` for both the source and destination folders.
- Consider completely disabling the file/folder moving functionality. In other words, it's currently based on how the Docker UI stores its output. It probably isn't a good idea to have TOMES Packager accommodate the user interface. Documentation can be used to help command line users of various TOMES software place outputs in the correct AIP structure. A graphical user interface could automatically create the correct AIP structure in the first place. In other words, Packager should perhaps only validate an existing AIP structure and create METS files.
- Force METS manifest templates to end in a given extension such as `.manifest.xml`, etc. This provides and easy way to check if an actual manifest template is being used to create the METS manifest.
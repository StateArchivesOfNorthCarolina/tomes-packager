# Ideas for Future Work

- Given how long it can take to build the METS manifest file with file checksums, consider adding logging statements that address how many files have been processed and how many more are left to process, i.e. "1 of 500 files have been processed ...".
- Clarify what is meant by "account_id" in the graphics.
- Add documentation on how to re-package contents (data already in the correct folder structure), e.g.:
	- `python3 packager.py foo ../tests/sample_files/ ../tests/sample_files/`
	- In other words, pass the parent folder of the containing AIP directory `foo` for both the source and destination folders.
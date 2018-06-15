# TOMES Archival Information Package
A TOMES Archival Information Package (AIP) has the following structure:

    [account_id]/                        
    |  eaxs/                             
    |  |  attachments/*.*             # EAXS-encoded attachments
    |  |  xml/                 
    |  |  |  [account_id].xml         # EAXS version of the account.
    |  |  |  [account_id]_tagged.xml  # "Tagged" version of EAXS.
    |  metadata/*.*                   # Optional data or administrative documents about the account (release forms, etc.)
    |  mime/*.*                       # EML or MBOX version of the account.
    |  pst/                
    |  |  [account_id].pst            # PST version of account (not required if account was exported as EML/MBOX).
    |  [account_id].mets.manifest     # Optional AIP manifest. Created by TOMES Packager. 
    |  [account_id].mets.xml          # Optional METS file with descriptive and/or preservation metadata. Created by TOMES Packager. 

In order to create a TOMES AIP, TOMES Packager requires the source data to be located in a *hot-folder*  that contains account files for one or more email accounts.

## Hot Folders

A hot-folder can have any root folder provided that the folder name does not contain whitespace. Likewise, account identifiers must not contain whitespace.

The internal structure of the hot-folder must be as follows:

    {root}/
    |  eaxs/                          # Each account subfolder contains any and all EAXS files and folders for the account.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  metadata/                      # Each account subfolder contains any and all optional data files and folders for the account.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  mime/                          # Each account subfolder contains any and all EML or MBOX files and folders for the account.
    |  |  {account_id_01}/*.*
    |  |  {account_id_02}/*.*
    |  pst/                           # Contains a single, optional PST file for each account.
    |  |  {account_id_01}.pst
    |  {account_id_02}.pdf            # "Stray" account files are supported if the filename prefix exactly matches the AIP account_id.
    |  {account_id_02}.xlsx           # Stray files are NOT RECOMMENDED. Use the "metadata" folder instead.

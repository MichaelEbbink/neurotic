.. _gdrive:

Configuring for Google Drive
============================

Downloading Google Drive files using *neurotic* requires some manual
configuration.

First, you must generate a "client credentials" file. The procedure is outlined
below and only needs to be completed once. The resultant file,
``credentials.json``, does not alone provide access to your Google account, but
it does identify you to Google as the owner of your installation of *neurotic*
when you use it to download files. For this reason, you are discouraged from
distributing this file to others.

Second, you must grant *neurotic* permission to access your Google Drive files
.......... TODO

.. _gdrive-credentials:

Generating a Client Credentials File
------------------------------------

1. Click the following link to open a web page. The web page is a tutorial for
   accessing Google Drive programmatically, as *neurotic* does. You will not
   need to follow the steps of this tutorial, but it does provide a convenient
   shortcut for generating the client credentials file.

        https://developers.google.com/drive/api/v3/quickstart/python

2. Click the button labeled "Enable the Drive API" in step 1 of the tutorial.
   You may be prompted to log into Google, and then a series of dialog boxes
   will take you through the configuration process. Follow these steps:

    a. Enter new project name: "neurotic".
    b. Accept terms of service, if necessary.
    c. Click "Next".
    d. Configure your OAuth client: Choose "Desktop app".
    e. Click "Create".
    f. Click "Download Client Configuration", which will download a file called
       ``credentials.json``.
    g. Click "Done".

4. Move the downloaded file, ``credentials.json``, into the
   ``.neurotic/gdrive-creds`` folder in your home folder:

    - Windows: ``C:\Users\<username>\.neurotic\gdrive-creds``
    - macOS: ``/Users/<username>/.neurotic/gdrive-creds``
    - Linux: ``/home/<username>/.neurotic/gdrive-creds``

.. _gdrive-permissions:

Granting Access Permissions
---------------------------

TODO

# Local SDK Folder

This repository is portable with its own vendored wrapper, but it does **not** commit the SGDK binaries.

Use one of these options on a fresh machine:

1. Set the `GDK` environment variable to an existing SGDK 2.11 installation.
2. Extract SGDK 2.11 into `./sdk/sgdk-2.11`.

The project wrapper will look for SGDK in this order:

1. `GDK`
2. `GDK_WIN`
3. `./sdk/sgdk-2.11`
4. `%USERPROFILE%\\sgdk\\sgdk-2.11`
5. `C:\\SGDK\\sgdk-2.11`
6. `C:\\sgdk\\sgdk-2.11`

If none of those paths contains `makefile.gen`, the build scripts will stop with a clear setup message.

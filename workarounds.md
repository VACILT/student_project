## Workarounds

### Problem 1:

installing pakages on the conda enviroment outputs the following error:
_Entry Point Not Found
The procedure entry point OPENSSL_sk_new_reserve could not be located in the dynamic link library XXXXX\Anaconda3\Library\bin\libssl-1_1-x64.dll_

### Solution 1:

_I copied the one in __Anaconda/DLLS__ and replaced that in __Anaconda/Library/bin__ and conda started working again, at least for now - I could install new packages again._

[Github Solution](https://github.com/conda/conda/issues/9003)

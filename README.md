# File Handling

<badges>[![version](https://img.shields.io/pypi/v/filehandling.svg)](https://pypi.org/project/filehandling/)
[![license](https://img.shields.io/pypi/l/filehandling.svg)](https://pypi.org/project/filehandling/)
[![pyversions](https://img.shields.io/pypi/pyversions/filehandling.svg)](https://pypi.org/project/filehandling/)  
[![donate](https://img.shields.io/badge/Donate-Paypal-0070ba.svg)](https://paypal.me/foxe6)
[![powered](https://img.shields.io/badge/Powered%20by-UTF8-red.svg)](https://paypal.me/foxe6)
[![made](https://img.shields.io/badge/Made%20with-PyCharm-red.svg)](https://paypal.me/foxe6)
</badges>

<i>Cross-platform file handling utilities.</i>

# Hierarchy
```
filehandling
|---- path
|   |---- temp_dir()
|   |---- abs_main_dir()
|   |---- abs_dir()
|   |---- join_path()
|   '---- get_cwd()
'---- file
    |---- read()
    |---- write()
    '---- Writer()
        '---- write()
```

# Example

## python
```python
from filehandling import *

# absolute directory of program main script file/executable
print(abs_main_dir())
# specify an inspect stack depth
print(abs_main_dir(depth=2))

# absolute directory of somefile
print(abs_dir("somefile"))

# join path and normalize it
print(join_path(abs_cwd(), "..", "somefile"))

# temporary directory of a bundled python application
print(temp_dir())

# absolute current working directory
print(get_cwd())

# read file content with automatic encoding detection
print(read("somefile"))
# specify an encoding
print(read("somefile", "ascii"))

# write content to file with attempts to use file queue
write("somefile", "a", "test\n")  # fallback to open()
write("somefile", "wb", b"test\n")  # fallback to open()

# Writer file queue
from encryptedsocket import SS
writer = Writer(server=True)
ss = SS(functions=writer.functions)
ss_thread = threading.Thread(target=ss.start)
ss_thread.daemon = True
ss_thread.start()
# use the writer
writer.write("somefile", "a", "test\n")
# use file queue
write("somefile", "wb", b"test\n")
```

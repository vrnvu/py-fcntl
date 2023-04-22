# py-fcntl

## Context


You can read this [lwn](https://lwn.net/Articles/667210/) article.

## Conclusion

In an ideal world your kernel would manage the file locking for you transparently.

A flag in the [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) syscall would be enough, imagine 'e' for exclusive:

``` python
def kernel_good_safe_file_access(file_path):
    with open(file_path, 'r+e') as f:
        content = f.read().strip()
        if content:
            value = int(content)
        else:
            value = 0
        value += 1
        f.seek(0)
        f.write(str(value))
        f.truncate()
```

Currently this is the output:

```sh
➜  py-fcntl python3 test_safe_file_access.py -n 50 --mode safe
➜  py-fcntl ls
.rw-r--r--@ 2.3k vrnvu 22 Apr 22:03 test_safe_file_access.py
.rw-r--r--@    2 vrnvu 22 Apr 22:03 testfilesafe
.rw-r--r--@    0 vrnvu 22 Apr 22:03 testfilesafe.lock

```

You need to polute user space with an ugly `*.lock` vs only having the file your process needs.

If you run the unsafe mode after removing the files:

```sh
➜  py-fcntl rm testfile*
➜  py-fcntl python3 test_safe_file_access.py -n 50 --mode unsafe
Traceback (most recent call last):
  File "/Users/vrnvu/repos/personal/py-fcntl/test_safe_file_access.py", line 97, in <module>
    test(num_processes=args.num_processes, target=target)
  File "/Users/vrnvu/repos/personal/py-fcntl/test_safe_file_access.py", line 81, in test
    assert value == str(num_processes), f"{value} != {num_processes}"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 44 != 50
```

So if you requiere more complex multi-process, multi-thread, multi-file orchestration, for example avoiding starvation, optimizing i/o, signaling... Things will get crappy in user space.

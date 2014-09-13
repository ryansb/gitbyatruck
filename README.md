## Git by a Truck

Based on the [original](http://dev.hubspot.com/blog/bid/57694/Git-by-a-Bus) git
by a bus, with enhancements to be able to process much larger repos.

## Installing

Note: this is developed for Python 3.3+. If you don't have that, good luck.

1. `pip install cffi`
1. Follow the [pygit2 instructions](http://www.pygit2.org/install.html) to get
   the libgit C bindings
1. Run `python setup.py install` in the `gitbyatruck` directory

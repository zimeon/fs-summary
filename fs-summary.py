#!/usr/bin/env python
"""Summary filesystem unser given dir.

"""
import datetime
import os
import os.path
import re
import sys
import time

class Summary(object):
    """Summary of filesystem."""

    def __init__(self):
        self.paths = []
        self.sizes_count = {}
        self.sizes_storage = {}
        self.year_count = {}
        self.year_storage = {}
        self.bytes = 0
        self.files = 0
        self.dirs = 0
        self.ignored = 0
        self.ignore_files = [ 'Thumbs.db', '.DS_Store' ]

    def add(self, path, filename):
        """Add path/filename to stats."""
        if (filename in self.ignore_files):
            self.ignored += 1
            return(0)
        self.files += 1
        filepath = os.path.join(path, filename)
        s = os.stat(filepath)
        self.bytes += s.st_size
        kb_size = (s.st_size + 1023) // 1024  #round up in kB
        mb_size = (s.st_size + 1048575) // 1048576  #round up in MB
        year = datetime.datetime.fromtimestamp(s.st_mtime).strftime('%Y')
        # accumulate data
        self.sizes_count[mb_size] = self.sizes_count.get(mb_size, 0) + 1
        self.sizes_storage[mb_size] = self.sizes_storage.get(mb_size, 0) + kb_size/1024.0
        self.year_count[year] = self.year_count.get(year, 0) + 1
        self.year_storage[year] = self.year_storage.get(year, 0) + kb_size/1024.0
        return(1)

    def clump_attr(self, attr, max_entries):
        """Clump data by doubling bin size until there are at most max_entries."""
        bin_size = 1
        d = getattr(self, attr)
        while (len(d)>max_entries):
            bin_size *= 2
            for (k,v) in d.items():
                k_new = (k // bin_size) * bin_size
                if (k != k_new):
                    d[k_new] = d.get(k_new, 0) + d[k]
                    del d[k]

    def dump_attr(self, attr, attr_formatter='d', col1='', col2=''):
        """Write date in dict of attribute attr."""
        print("%-16s %-8s" % ('#'+col1, col2))
        d = getattr(self, attr)
        fmt_str = "%-16" + attr_formatter + " %-8d"
        for k in sorted(d.keys()):
            print(fmt_str % (k, int(d[k]+0.5)))

    def scan(self, root):
        """Scan files and dirs under root."""
        self.paths.append(root)
        for path, dirs, files in os.walk(root, topdown=True):
            self.dirs += 1
            for filename in files:
                self.add(path, filename)

    def print_summary(self):
        print("\n# Scan summary\n")
        print("Run on: %s" % (datetime.datetime.now().strftime("%Y-%m-%d")))
        print("Paths scanned: %s" % (str(self.paths)))
        print("Dirs scanned: %d" % (self.dirs))
        print("Files included: %d  (total %.1fGB)" % (self.files, (self.bytes / 1073741824)))
        print("File ignored: %d  (patterns ignored %s)" % (self.ignored, str(self.ignore_files)))
        print("\n## File sizes (count)\n")
        self.clump_attr('sizes_count', 50)
        self.dump_attr('sizes_count', 'd', 'filesize(MB)', 'num_files')
        print("\n## File sizes (storage)\n")
        self.clump_attr('sizes_storage', 50)
        self.dump_attr('sizes_storage', 'd', 'filesize(MB)', 'storage(MB)')
        print("\n## Files by year (count)\n")
        self.dump_attr('year_count', 's', 'year', 'num_files')
        print("\n## File by year (storage)\n")
        self.dump_attr('year_storage', 's', 'year', 'storage(MB)')

summary = Summary()
for path in sys.argv[1:]:
    print("Scanning %s" % (path))
    summary.scan(path)
    summary.print_summary()


#!/usr/bin/env python3

import os
import tempfile
import stat
import shutil

class Path:
    def __init__(self, path):
        if type(path) == type(""):
            path = os.path.normcase(path)
            path = os.path.normpath(path)
            if path.startswith("~"):
                path = os.path.expanduser(path)
            if "%" in path or "$" in path:
                path = os.path.expandvars(path)
            if not os.path.isabs(path): # Relative path
                path = os.path.abspath(path)
            self.path = Path.split(path)
        elif type(path) in (type(()), type([])):
            self.path = path[:]
        else:
            self.path = path.path[:]

    def __add__(self, other):
        if type(other) == type(""):
            other = Path.split(other)
        elif hasattr(other, "path"):
            other = other.path
        return Path(Path.join(self.path + other))

    def __hash__(self):
        return hash(self.path)

    def __bool__(self):
        return self.exists()

    def __eq__(self, other):
        return str(self) == str(other)
    
    def __len__(self):
        return len(self.path)

    def __getitem__(self, key):
        if type(key) == type(""):
            return Path(self.path + [key])
        elif type(key) == type(0):
            if key == -1:
                return Path(self)
            else:
                return Path(self.path[:key + 1])
        elif type(key) == type(slice(0, 0, 0)):
            return Path(self.path[key])
        raise IndexError

    def __setitem__(self, key, value):
        if type(value) == type(""):
            value = Path.split(value)

        while value[0] == "":
            value = value[1:]

        if type(key) == type(slice(0, 0, 0)):
            self.path[key] = value
        else:
            if key == -1:
                self.path[key:] = value
            else:
                self.path[key:key+1] = value
    
    def __delitem__(self, key):
        del self.path[key]

    def __contains__(self, key):
        return self + key

    def __str__(self):
        return Path.join(self.path)

    def __repr__(self):
        return "Path({0})".format(str(self))

    def __enter__(self):
        self.old_path = Path.current()
        Path.current(self)
        return self

    def __exit__(self, *args):
        Path.current(self.old_path)
    
    def real(self):
        return Path(os.path.realpath(Path.join(self.path)))

    def get(self):
        path = Path.join(self.path)
        if os.path.isfile(path):
            return File(self)
        elif os.path.isdir(path):
            return Dir(self)
        return File(path) # Eh, we need to return something...

    def exists(self):
        return os.path.exists(str(self))

    def type(self):
        l = []
        if os.path.isfile(str(self)):
            l.append("file")
        elif os.path.isdir(str(self)):
            l.append("dir")
        if os.path.islink(str(self)):
            l.append("link")
        if os.path.ismount(str(self)):
            l.append("mount")

        return l

    def link(self, dest, type="soft"):
        if type == "hard":
            os.link(str(dest), str(self))
        else:
            os.symlink(str(dest), str(self))

    def link_from(self, source, type="soft"):
        if not isinstance(source, Path):
            source = Path(source)

        source.link(self, type)

    @staticmethod
    def split(path, l=None):
        if not l:
            l = []

        try:
            h, t = os.path.split(path)
            l.insert(0, t)
            if h != path:
                Path.split(h, l)
            else:
                l[0] = h
        except:
            pass

        return l

    @staticmethod
    def join(path):
        return os.path.join(*path)

    @staticmethod
    def current(new=None):
        if new:
            new = str(Path(new))
            os.chdir(new)
        return Path(os.getcwd())

    @staticmethod
    def setroot(root):
        os.chroot(root)

class FSObject:
    def __init__(self, path):
        self.path = path

    def access(self, mode=None):
        if mode is None:
            s = ""
            if self.access("r"):
                s += "r"
            if self.access("w"):
                s += "w"
            if self.access("x"):
                s += "x"
            return s
        
        s = 0
        if "r" in mode:
            s |= os.R_OK
        if "w" in mode:
            s |= os.W_OK
        if "x" in mode:
            s |= os.X_OK
        
        return os.access(str(self.path), s)

    last_access = lambda self: os.path.getatime(str(self.path))
    last_change = lambda self: os.path.getmtime(str(self.path))
    ctime = lambda self: os.path.getctime(str(self.path))

    def move(self, new):
        if isinstance(new, Path):
            shutil.move(str(self.path), str(new))
            self.path = new
        elif isinstance(new, File):
            shutil.move(str(self.path), str(new.path))
            self.path = new.path
        else:
            shutil.move(str(self.path), new)
            self.path = Path(new)

    def rename(self, new):
        t = Path(self.path)
        t[-1] = new
        os.rename(str(self.path), str(t))
        self.path = new

    def chown(self, uid=-1, gid=-1):
        os.chown(str(self.path), uid, gid)

    def chmod(self, *mode):
        """
        Pass permissions of user, group, other, extra bits*
        Where extra bits may include "uid", "gid", and "vtx"
        """

        mode = list(mode)
        
        while len(mode) < 3:
            mode.append("")
        
        s = 0

        if any("r" in i for i in mode) > 0:
            s |= stat.S_IREAD
        elif any("w" in i for i in mode) > 0:
            s |= stat.S_IWRITE

        if "r" in mode[0]:
            s |= stat.S_IRUSR
        if "w" in mode[0]:
            s |= stat.S_IWUSR
        if "x" in mode[0]:
            s |= stat.S_IXUSR
            
        if "r" in mode[1]:
            s |= stat.S_IRGRP
        if "w" in mode[1]:
            s |= stat.S_IWGRP
        if "x" in mode[1]:
            s |= stat.S_IXGRP
            
        if "r" in mode[2]:
            s |= stat.S_IROTH
        if "w" in mode[2]:
            s |= stat.S_IWOTH
        if "x" in mode[2]:
            s |= stat.S_IXOTH

        if "gid" in mode:
            s |= stat.S_ISGID
        if "uid" in mode:
            s |= stat.S_ISUID
        if "vtx" in mode:
            s |= stat.S_ISVTX

        os.chmod(str(self.path), s)

    def __eq__(self, other):
        if type(other) == type(""):
            other = FSObject(other)
        
        return os.path.samefile(str(self.path), str(other.path))

    def chflags(self, *flags):
        s = 0
        
        if "no dump" in flags:
            s |= stat.UF_NODUMP
        if "immutable" in flags:
            s |= stat.UF_IMMUTABLE
        if "append" in flags:
            s |= stat.UF_APPEND
        if "opaque" in flags:
            s |= stat.UF_OPAQUE
        if "no unlink" in flags:
            s |= stat.UF_NOUNLINK
        if "archived" in flags:
            s |= stat.SF_ARCHIVED
        if "system immutable" in flags:
            s |= stat.SF_IMMUTABLE
        if "system append" in flags:
            s |= stat.SF_APPEND
        if "system no unlink" in flags:
            s |= stat.SF_NOUNLINK
        if "snapshot" in flags:
            s |= stat.SF_SNAPSHOT

        os.chflags(self.path, s)

    def __name(self):
        return self.path.path[-1]
    
    name = property(__name, lambda self, new: self.rename(new))
    
class File(FSObject):
    def __init__(self, path=None):
        if path:
            if type(path) != type(""):
                path = str(path)
            self.path = Path(path)
        else:
            t = tempfile.mkstemp()
            self.path = Path(t[1])

        FSObject.__init__(self, self.path)

    def open(self, mode="r"):
        self.file = open(str(self.path), mode)
        return self.file

    def size(self):
        return os.path.getsize(str(self.path))

    def create(self):
        open(str(self.path), "w").close()
    
    def delete(self):
        os.remove(str(self.path))

    def copy(self, dest):
        if isinstance(dest, File):
            dest = str(dest.path)
        
        shutil.copy2(str(self.path), str(dest))

    def __gt__(self, other):
        if isinstance(other, Dir):
            return False
        else:
            try:
                return self.name > other.name
            except:
                return True

class Dir(FSObject):
    def __init__(self, path):
        if path:
            if type(path) != type(""):
                path = str(path)
            self.path = Path(path)
        else:
            t = tempfile.mkdtemp()
            self.path = Path(t)

        FSObject.__init__(self, self.path)

    def __iter__(self):
        return self.files().__iter__()

    def files(self):
        l = os.listdir(str(self.path))
        r = []

        for i in l:
            p = Path(self.path.path + [i])
            r.append(p.get())

        r.sort()
        return r

    def create(self, mode=0o777):
        os.makedirs(str(self.path), mode)

    def delete(self):
        shutil.rmtree(self.path.real())

    def copy(self, dest, symlinks=True):
        if isinstance(dest, Dir):
            dest = str(dest.path)
        
        shutil.copytree(str(self.path), str(dest), symlinks)
        
    def walk(self, *args, **kwargs):
        """ Same arguments as os.walk """

        os.walk(str(self.path), *args, **kwargs)

    def __gt__(self, other):
        if isinstance(other, File):
            return True
        else:
            try:
                return self.name > other.name
            except:
                return True

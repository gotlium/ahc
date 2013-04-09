from subprocess import Popen, PIPE
from shutil import rmtree, move
import os

from helpers import fileExists, system, system_by_code


ECHO = "/bin/echo"


class EncFS(object):
    def __init__(self, crypt, path, config):
        self.crypt = crypt
        self.path = path
        self.password = config['password']
        self.idle = config['idle']
        self.tempdir = config['tempdir']
        self.bin = config['bin']
        self.fusermount = config['bin_fusermount']
        system('modprobe fuse')

    def encrypt(self):
        if not fileExists(self.crypt):
            os.makedirs(self.crypt, 0755)

            if not fileExists(self.path):
                os.makedirs(self.path, 0755)

            if len(os.listdir(self.path)) > 0:
                if fileExists(self.tempdir):
                    rmtree(self.tempdir)
                os.mkdir(self.tempdir)
                for f in os.listdir(self.path):
                    move(os.path.join(self.path, f),
                         os.path.join(self.tempdir, f))
                rmtree(self.path)
                os.mkdir(self.path)

            p1 = Popen([ECHO, "-e", "\"p\n%s\n\"" % self.password],
                       stdout=PIPE)
            p2 = Popen([self.bin, "-S", self.crypt, self.path, "--public"],
                       stdin=p1.stdout, stdout=PIPE)
            p2.communicate()
            if p2.poll() is not 0:
                raise Exception('Bad Password!')

            if fileExists(self.tempdir) and len(os.listdir(self.tempdir)) > 0:
                for f in os.listdir(self.tempdir):
                    move(os.path.join(self.tempdir, f),
                         os.path.join(self.path, f))
                rmtree(self.tempdir)
            return True
        return False

    def mount(self):
        p1 = Popen([ECHO, self.password], stdout=PIPE)
        if self.idle:
            p2 = Popen(
                [self.bin, "-S", self.crypt, "-i", self.idle,
                 self.path, "--public", "--", "-o", "nonempty"],
                stdin=p1.stdout, stdout=PIPE
            )
        else:
            p2 = Popen(
                [self.bin, "-S", self.crypt, self.path, "--public",
                 "--", "-o", "nonempty"],
                stdin=p1.stdout, stdout=PIPE
            )
        p2.communicate()
        if p2.poll() is not 0:
            raise Exception('Bad Password!')

    def umount(self):
        system_by_code(
            "%s -z -u %s 1> /dev/null" % (self.fusermount, self.path))

    def decrypt(self):
        out = system('mount|grep %s' % self.path)
        if not out or not len(out):
            self.mount()
        if fileExists(self.tempdir):
            rmtree(self.tempdir)
        os.mkdir(self.tempdir)
        for f in os.listdir(self.path):
            move(os.path.join(self.path, f), os.path.join(self.tempdir, f))
        self.umount()
        rmtree(self.crypt)
        for f in os.listdir(self.tempdir):
            move(os.path.join(self.tempdir, f), os.path.join(self.path, f))

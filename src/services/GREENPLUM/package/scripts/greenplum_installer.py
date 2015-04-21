from os import path
import os
import io
import re
import zipfile, tarfile
from StringIO import StringIO
import urllib

class GreenplumDistributed(object):
    @staticmethod
    def from_source(installer_path, tmp_dir=None):
        """Create a GreenplumDistributed from a source path.

        installer_path -- Path to the distributed zip archive.
        tmp_dir -- Temporary directory to store the archive if it needs to be downloaded from a URL.  Optional.

        The installer_path can be either a local filepath or URL (one which can be downloaded by urllib).
        """

        if tmp_dir == None:
            import tempfile
            tmp_dir = tempfile.mkdtemp()

        # Attempt to locate locallay
        if path.exists(installer_path):
            return GreenplumDistributed(installer_path)

        # Attempt to download URL
        try:
            tmp_path = path.join(tmp_dir, 'greenplum-db.zip')
            urllib.urlretrieve(installer_path, tmp_path)

            return GreenplumDistributed(tmp_path)
        except IOError:
            pass

        # Default to erroring if none of the above retrieval methods were successful.
        raise LookupError('Could not find greenplum installer at %s' % installer_path)

    def __init__(self, path):
        self.__path = path
        self.__archive = None

    def __enter__(self):
        # Open and cache installer archive handler.
        return self.get_installer()

    def __exit__(self):
        self.close()

    def __del__(self):
        self.close()

    def get_installer(self):
        installer_file = GreenplumInstaller.find_installer_name(self.__get_archive().infolist())

        if len(installer_file) != 1:
            raise StandardError('Incorrect number of .bin files found in referenced greenplum installation archive.  Found %s, expected 1.' % len(installer_file))

        installer_file = installer_file[0]

        return GreenplumInstaller(installer_file.filename, self.__get_archive().read(installer_file))        

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __get_archive(self):
        if self.__archive == None:
            self.__archive = zipfile.ZipFile(self.__path, 'r')

        return self.__archive

class GreenplumInstaller(object):
    @staticmethod
    def find_installer_name(filelist):
        """
        Given a list of ZipFileInfo objects, return the ones which would install greenplum.
        """
        return filter(lambda f: f.filename.endswith('.bin'), filelist)

    def __init__(self, filename, fileContents = None):
        self.__filename = filename
        self.__fileContents = fileContents
        self.__version = self.__parse_version(filename)

    def __enter__(self):
        return self.__get_archive()

    def __exit__(self):
        self.close()

    def install_to(self, destination):
        archive = self.__get_archive()
        archive.extractall(destination)
        archive.close()

    def get_name(self):
        return self.__filename

    def get_version(self):
        return self.__version

    def close(self):
        if self.__archive != None:
            self.__archive.close()

    def __get_archive(self):
        installer_script_stream = StringIO(self.get_file_contents())

        # Seek to the line before the archive's binary data starts.
        seekedToLine = False
        for line in iter(installer_script_stream.readline, b''):
            if line == "__END_HEADER__\n":
                seekedToLine = True
                break

        if not seekedToLine:
            raise StandardError('Could not find archive contents, archive extraction failed.')

        # Return a TarFile of the remaining lines in the installer script.
        return tarfile.open(fileobj = installer_script_stream, mode = "r:gz")

    def __parse_version(self, filename):
        try:
            matches = re.search(r"greenplum-db-([0-9\.]+)[^/]+\.bin", filename)

            return matches.group(1)
        except StandardError:
            raise StandardError('Could not parse greenplum version from given filename %s' % filename)
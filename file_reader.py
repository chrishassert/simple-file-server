import os
import mimetypes as mime
# Code written by Christopher Hassert (ch8jd)
# On my honor as student, I have neither given nor received aid on this assignment


class FileReader:

    def __init__(self):
        pass

    def get(self, filepath, cookies):
        '''
        Returns a binary string of the file contents, or None.
        '''
        path_name = os.path.abspath(filepath)
        if(os.path.isfile(filepath)):
            f = open(path_name, 'rb')
            fileToSend = f.read()
            f.close()
            return fileToSend
        else:
            return None

    def head(self, filepath, cookies):
        '''
        Returns the size to be returned, or None.
        '''

        if(os.path.exists(filepath)):
            return os.path.getsize(filepath)
        else:
            return None

    def checkPath(self, filepath):
        '''
        Returns a boolean value if a directory exists
        '''
        if(os.path.isdir(filepath)):
            return True
        else:
            return False

    def getMime(self, filepath):
        '''
        Returns a mimetype string if the file exists, or None.
        '''
        #path_name = os.path.abspath(filepath)
        if(os.path.isfile(filepath)):
            return str(mime.guess_type(filepath)[0])
        else:
            return None

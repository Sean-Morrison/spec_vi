

class VI_log():
    def __init__(self, filename, append = False):
        opentype = 'a' if append else 'w'
        self._logfile = open(filename,opentype)
    def log(self,string):
        self._logfile.write(string+'\n')
    def close(self):
        self._logfile.close()

class Logger:
    def __init__(self, filename):
        self.f = open(filename, 'w')

    def write(self, s):
        self.f.write(s)

    def writeline(self, s):
        self.f.write(s)
        self.f.write('\n')

    def close(self):
        self.f.close()

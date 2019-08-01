import os
DIR = 'ransomware/'
os.execvp('zcat', ['zcat'] + [DIR + file for file in sorted(os.listdir('ransomware'))])

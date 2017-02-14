from sqlalchemy import *
from sqlalchemy.orm import *
from trac.attachment import Attachment
from optparse import OptionParser
import os
import sys
import paramiko

parser = OptionParser()
parser.add_option('--host', dest='host', action='store', type='string',
                  help='SFTP host')
parser.add_option('--path', dest='path', action='store', type='string',
                  help='SFTP path')
parser.add_option('--username', dest='username', action='store', type='string',
                  help='SFTP login username')
parser.add_option('--password', dest='password', action='store', type='string',
                  help='SFTP login password')


TRACDB = "/home/kent/tracdb/trac.db"
OUTPUTDIR = "/home/kent/loft.wiki/tracattachments"
PREFIX = "/home/kbower/trac/files/attachments/wiki"


class Att(object):
    def __init__(self, row):
        self.wikititle = row.id
        self.filename = row.filename

    def __unicode__(self):
        return u"%s: %s: %s" % (self.fullpath(), self.wikititle, self.filename)

    def fullpath(self):
        path = Attachment._get_hashed_filename(self.wikititle)
        return u"%s/%s/%s/%s" % (
            PREFIX,
            path[:3],
            path,
            Attachment._get_hashed_filename(self.filename)
        )

    @property
    def shorttitle(self):
        return self.wikititle.split('/')[-1]

    def outputpath(self):
        return "%s/%s" % (OUTPUTDIR, self.shorttitle)

    def fulloutputpath(self):
        return "%s/%s" % (self.outputpath(), self.filename)


class Downloader(object):

    def __init__(self, host, username, password):
        self.engine = create_engine('sqlite:///%s' % TRACDB, echo=True and False)
        self.metadata = MetaData(self.engine)
        self.metadata.reflect()
        self.att_table = self.metadata.tables['attachment']
        self.host = host or "retailarchitects.com:30000"
        self.username = username or "kbower"
        self.password = password

    def download_files(self):
        """
        Log in to the SFTP server using the username and password
        provided and download the specified files.
        """
        stmt = self.att_table.select()\
            .where(self.att_table.c.type == 'wiki')
        transport = paramiko.Transport(self.host)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        for a in self.engine.execute(stmt).fetchall():
            if not a.size or \
               a.size > 10000000 or \
               a.id == 'PasswordDatabase':
                print u"SKIPPING %s" % att
                continue
            att = Att(a)
            print u"Downloading %s" % att
            destdir = att.outputpath()
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            sftp.get(att.fullpath(), att.fulloutputpath())


if __name__ == '__main__':
    options, args = parser.parse_args()
    if args:
        parser.print_help()
        sys.exit(1)        
    d = Downloader(options.host, options.username, options.password)
    d.download_files()        

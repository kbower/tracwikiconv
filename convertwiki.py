from sqlalchemy import *
from sqlalchemy.orm import *
from trac.wiki.formatter import trac_to_github

GITPATH = "/home/kent/loft"
TRACDB = "/home/kent/tracdb/trac.db"
OUTPUTDIR = "/home/kent/loft.wiki"
ATTACH = u"""* [{filename}]({link})"""
SKIP = set([
    'PasswordDatabase',
    'ElDoradoInfo',
    'IvanSmithInfo',
    'KanesInfo',
    'LevinInfo',
    'MiskellyInfo',
    'MorrisInfo',
    'SlumberlandInfo',
    'SteinhafelsInfo',
])

engine = create_engine('sqlite:///%s' % TRACDB, echo=True and False)
metadata = MetaData(engine)
metadata.reflect()
wiki_table = metadata.tables['wiki']
att_table = metadata.tables['attachment']


def add_attachments_section(wikititle, shortname, page):
    """
    ### Attachments
    * [middleware.py](tracattachments/WinpdbPythonDebugger/middleware.py)
    """
    attstmt = att_table.select()\
        .where(and_(
            att_table.c.type == 'wiki',
            att_table.c.id == wikititle))\
        .order_by(att_table.c.time)
    attachments = []
    for a in engine.execute(attstmt).fetchall():
        link = u"tracattachments/{wikiname}/{filename}"\
            .format(filename=a.filename, wikiname=shortname)
        if link in page:
            # included in actual md text
            continue
        attachments.append(ATTACH.format(filename=a.filename, 
            link=link))
    if attachments:
        return "\n### Attachments\n" + "\n".join(attachments)
    return ''

stmt = select([distinct(wiki_table.c.name)]).where(wiki_table.c.author != 'trac')

wikinames = set(r.name for r in engine.execute(stmt).fetchall())
wikishortnames = [n.split('/')[-1] for n in wikinames]

for wikititle in sorted(wikinames - SKIP):
    print "loading %s" % wikititle
    shortname = wikititle.split('/')[-1]
    #if wikititle == 'AssemblyDesign': import pdb; pdb.set_trace()
    #SELECT text FROM wiki 
    #WHERE name=%s
    #ORDER BY version DESC 
    #LIMIT 1    
    stmt = select([wiki_table.c.text])\
        .where(wiki_table.c.name == wikititle)\
        .order_by(desc(wiki_table.c.version))\
        .limit(1)
    txt = engine.execute(stmt).scalar()
    txt = trac_to_github(txt, shortname, wikishortnames, GITPATH, SKIP)
    txt += add_attachments_section(wikititle, shortname, txt)
    # Write file
    filename = "%s/%s.md" % (OUTPUTDIR, shortname)
    with open(filename, 'w') as outfile:
        print "writing %s" % filename
        outfile.write(txt.encode('utf-8'))


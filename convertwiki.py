from sqlalchemy import *
from sqlalchemy.orm import *
from trac.wiki.formatter import trac_to_github

GITPATH = "/home/kent/loft"
TRACDB = "/home/kent/tracdb/trac.db"
OUTPUTDIR = "/home/kent/loft.wiki"

engine = create_engine('sqlite:///%s' % TRACDB, echo=True and False)
metadata = MetaData(engine)
metadata.reflect()

def _convertWikiToMd(txt, currentticket):
    from trac.wiki.formatter import trac_to_github
    return trac_to_github(txt, _gitpath, currentticket)

wiki_table = metadata.tables['wiki']

stmt = select([distinct(wiki_table.c.name)]).where(wiki_table.c.author != 'trac')

wikinames = set(r.name for r in engine.execute(stmt).fetchall())
wikishortnames = [n.split('/')[-1] for n in wikinames]

for wikititle in sorted(wikinames - set('PasswordDatabase')):
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
    txt = trac_to_github(txt, shortname, wikishortnames, GITPATH)
    # Write file
    filename = "%s/%s.md" % (OUTPUTDIR, shortname)
    with open(filename, 'w') as outfile:
        print "writing %s" % filename
        outfile.write(txt.encode('utf-8'))


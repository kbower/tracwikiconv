from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///../tracdb/trac.db', echo=True)
metadata = MetaData(engine)
metadata.reflect()

def _convertWikiToMd(txt, currentticket):
    from trac.wiki.formatter import trac_to_github
    return trac_to_github(txt, _gitpath, currentticket)

wiki_table = metadata.tables['wiki']

stmt = select([distinct(wiki_table.c.name)])

for name in engine.execute(stmt).fetchall():
    print name.name

import pdb; pdb.set_trace()


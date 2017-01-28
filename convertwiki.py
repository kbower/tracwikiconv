from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
metadata.reflect()


def _convertWikiToMd(txt, currentticket):
    from trac.wiki.formatter import trac_to_github
    return trac_to_github(txt, _gitpath, currentticket)

import pdb; pdb.set_trace()


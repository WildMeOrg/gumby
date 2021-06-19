import gumby


def migrate(doc):
    # Assign a birth and death date
    doc.birth, doc.death = gumby.random_animate_timespan()
    return doc

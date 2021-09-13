def migrate(doc):
    # Squash the taxonomy
    doc.taxonomy = ' '.join([doc.genus, doc.species])
    del doc.genus
    del doc.species
    for enc_doc in doc.encounters:
        enc_doc.taxonomy = ' '.join([enc_doc.genus, enc_doc.species])
        del enc_doc.genus
        del enc_doc.species
    return doc

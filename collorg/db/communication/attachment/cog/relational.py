# DIRECT
def _get_data(self):
    data_ = self.db.table('collorg.core.oid_table')
    data_.cog_oid_.value = self.data_
    return data_
def _set_data(self, data_):
    self.data_.value = data_.cog_oid_

_data_ = property(
    _get_data, _set_data)

def _get_ref(self):
    ref_ = self.db.table('collorg.communication.file')
    ref_.cog_oid_.value = self.ref_
    return ref_
def _set_ref(self, ref_):
    self.ref_.value = ref_.cog_oid_

_ref_ = property(
    _get_ref, _set_ref)

def _get_author(self):
    author_ = self.db.table('collorg.actor.user')
    author_.cog_oid_.value = self.author_
    return author_
def _set_author(self, author_):
    self.author_.value = author_.cog_oid_

_author_ = property(
    _get_author, _set_author)


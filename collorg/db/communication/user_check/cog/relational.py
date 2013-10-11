# DIRECT
def _get_communication_object(self):
    communication_object_ = self.db.table('collorg.core.oid_table')
    communication_object_.cog_oid_.set_intention(self.communication_object_)
    return communication_object_
def _set_communication_object(self, communication_object_):
    self.communication_object_.set_intention(communication_object_.cog_oid_)

_communication_object_ = property(
    _get_communication_object, _set_communication_object)

def _get_user(self):
    user_ = self.db.table('collorg.actor.user')
    user_.cog_oid_.set_intention(self.user_)
    return user_
def _set_user(self, user_):
    self.user_.set_intention(user_.cog_oid_)

_user_ = property(
    _get_user, _set_user)


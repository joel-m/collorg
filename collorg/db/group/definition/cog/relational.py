# DIRECT
def _get_function(self):
    function_ = self.db.table('collorg.actor.function')
    function_.cog_oid_.value = self.function_
    return function_
def _set_function(self, function_):
    self.function_.value = function_.cog_oid_

_function_ = property(
    _get_function, _set_function)

def _get_group(self):
    group_ = self.db.table('collorg.group.group')
    group_.cog_oid_.value = self.group_
    return group_
def _set_group(self, group_):
    self.group_.value = group_.cog_oid_

_group_ = property(
    _get_group, _set_group)


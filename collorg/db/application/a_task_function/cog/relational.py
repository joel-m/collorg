# DIRECT
def _get_function(self):
    function_ = self.db.table('collorg.actor.function')
    function_.cog_oid_.set_intention(self.function_)
    return function_
def _set_function(self, function_):
    self.function_.set_intention(function_.cog_oid_)

_function_ = property(
    _get_function, _set_function)

def _get_task(self):
    task_ = self.db.table('collorg.application.task')
    task_.cog_oid_.set_intention(self.task_)
    return task_
def _set_task(self, task_):
    self.task_.set_intention(task_.cog_oid_)

_task_ = property(
    _get_task, _set_task)


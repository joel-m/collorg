#-*- coding: UTF-8 -*-

from collorg.db.core.base_table import Base_table

class Goal(Base_table):
    #>>> AUTO_COG REL_PART. DO NOT EDIT!
    _cog_schemaname = 'collorg.activity'
    _cog_tablename = 'goal'
    _cog_templates_loaded = False

    from .cog import relational as cog_r
    # REVERSE
    _rev_a_task_goal_ = cog_r._rev_a_task_goal_
    _task__s_ = cog_r._task__s_ # _rev_a_task_goal_._task_
    #<<< AUTO_COG REL_PART. Your code goes after
    def __init__(self, db, **kwargs):
        #>>> AUTO_COG DOC. DO NOT EDIT
        """
        * _db : ref. to database. usage: self.db.table(fqtn)
        fields list:
        * cog_oid_ : uuid, uniq, not null
        * cog_fqtn_ : text, not null
        * cog_signature_ : text, inherited
        * cog_test_ : bool, inherited
        * cog_creat_date_ : timestamp, inherited
        * cog_modif_date_ : timestamp, inherited
        * cog_presentation_ : wiki, inherited
        * cog_state_ : text, inherited
        * name_ : string, PK, not null
        * description_ : wiki
        """
        #<<< AUTO_COG DOC. Your code goes after
        super(Goal, self).__init__(db, **kwargs)


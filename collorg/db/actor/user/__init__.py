#-*- coding: utf-8 -*-
### Copyright © 2011 Joël Maïzi <joel.maizi@lirmm.fr>
### This file is part of collorg

### collorg is free software: you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation, either version 3 of the License, or
### (at your option) any later version.

### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.

### You should have received a copy of the GNU General Public License
### along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collorg.db.actor.actor import Actor
from collorg.db.group._groupable import Groupable
import uuid
import hashlib

try:
    import ldap
    ldap_ = True
except:
    ldap_ = False

class NoPasswdError(Exception): pass
class ToManyAccountError(Exception): pass
class SessionKeyError(Exception): pass

class User(Actor, Groupable):
    #>>> AUTO_COG REL_PART. DO NOT EDIT!
    _cog_schemaname = 'collorg.actor'
    _cog_tablename = 'user'
    _cog_templates_loaded = False

    from .cog import relational as cog_r
    # DIRECT
    _ldap_ = cog_r._ldap_
    _photo_ = cog_r._photo_
    # REVERSE
    _rev_a_user_category_ = cog_r._rev_a_user_category_
    _rev_post_ = cog_r._rev_post_
    _rev_log_ = cog_r._rev_log_
    _rev_user_check_ = cog_r._rev_user_check_
    _rev_topic_ = cog_r._rev_topic_
    _rev_access_ = cog_r._rev_access_
    _rev_bookmark_ = cog_r._rev_bookmark_
    _rev_attachment_ = cog_r._rev_attachment_
    _rev_file_ = cog_r._rev_file_
    _rev_session_ = cog_r._rev_session_
    _rev_follow_up_ = cog_r._rev_follow_up_
    _rev_relation_me_ = cog_r._rev_relation_me_
    _rev_relation_my_relation_ = cog_r._rev_relation_my_relation_
    _rev_comment_ = cog_r._rev_comment_
    _rev_a_post_data_ = cog_r._rev_a_post_data_
    #<<< AUTO_COG REL_PART. Your code goes after
    _is_cog_user = True
    def __init__(self, db, **kwargs):
        #>>> AUTO_COG DOC. DO NOT EDIT
        """
        * _db : ref. to database. usage: self.db.table(fqtn)
        fields list:
        * cog_oid_ : c_oid, uniq, not null
        * cog_fqtn_ : c_fqtn, not null
        * cog_signature_ : text, inherited
        * cog_test_ : bool, inherited
        * cog_creat_date_ : timestamp, inherited
        * cog_modif_date_ : timestamp, inherited
        * cog_environment_ : c_oid, inherited
        * cog_state_ : text, inherited
        * first_name_ : string, not null
        * last_name_ : string, not null
        * gender_ : bpchar
        * birthday_ : date
        * email_ : email, PK, not null
        * pseudo_ : text, uniq
        * password_ : password, not null
        * validation_key_ : c_oid, not null
        * valid_account_ : bool
        * system_account_ : bool
        * ldap_ : c_oid, FK
        * photo_ : c_oid, FK
        * url_ : url
        * alien_ : bool
        """
        #<<< AUTO_COG DOC. Your code goes after
        self.__groups = None
        super(User, self).__init__(db, **kwargs)

    @property
    def cog_session_key(self):
        assert self.cog_oid_.value
        return self.db._cog_controller._session.key_

    @property
    def cog_group_name(self):
        return "%s %s's private group" % (self.first_name_, self.last_name_)

    @property
    def _cog_label(self):
        return ["{} {}", self.first_name_, self.last_name_]

    def is_(self, user):
        if user is None:
            return False
        return self.cog_oid_.value == user.cog_oid_.value

    def __grant_self_access(self):
        access = self.db.table('collorg.access.access')
        access.grant(user=self, data=self)

    def __encrypt_password(self, password):
        salt = uuid.uuid4()
        salted_password = "%s%s" % (salt, password)
        return (salt,
                hashlib.sha256(salted_password.encode('utf-8')).hexdigest())

    def new_account(self, **kwargs):
        self.db.set_auto_commit(False)
        new = self()
        new.email_.value = kwargs['email_'] or None
        if not new.is_empty():
            raise RuntimeError("an account already exists for this email")
        new.pseudo_.value = kwargs.get('pseudo_', None)
        new.first_name_.value = kwargs['first_name_'] or " "
        new.last_name_.value = kwargs['last_name_'] or " "
        new.ldap_.value = kwargs.get('ldap_', None)
        salt, enc_password = self.__encrypt_password(
            kwargs.get('password_', uuid.uuid4()))
        new.password_.value = enc_password
        new.validation_key_.value = salt
        new.insert()
        topic = new._rev_topic_
        topic.title_.value = "{} {}".format(
            kwargs['first_name_'], kwargs['last_name_'])
        topic.text_.value = ''
        topic.path_info_.value = ''
        topic.author_.value = new.cog_oid_
        topic.cog_environment_.value = new.cog_oid_
        topic.insert()
        new.grant_access(new, True)
        new.grant_access(topic, True)
        self.db.commit()
        return new

    def root_topic(self):
        topic = self._rev_topic_
        topic.path_info_.value = ''
        topic.cog_environment_.value = self.cog_oid_
        return topic

    def remove_account(self):
        """
        Removes the account and all contributions
        """
        self._rev_access_.delete()
        self._rev_a_user_category_.delete()
        self._rev_comment_.delete()
        self._rev_post_.delete()
        self.delete()

    def login(self, login, password, domain):
        """
        returns the key of the session (None on failure)
        """
        auth_result = self.__authentication(login, password, domain)
        if auth_result:
            cog_session = self._cog_controller.set_cookie('cog_session')
            self.__grant_self_access()
            session = self.db.table('collorg.web.session')
            session.new(self, cog_session)
            self._cog_controller.set_user(self.cog_oid_.value)
            return cog_session
        return auth_result

    def logout(self):
        sess = self._rev_session_
        key = self._cog_controller.get_cookie('cog_session')
        self._cog_controller.delete_cookie('cog_session')
        self._cog_controller._user = None
        if key is not None:
            sess.key_.value = key
            if not sess.is_empty():
                sess.delete()
                self._cog_controller.del_user(key)
            f_ = self.db.table('collorg.communication.file')
            f_.remove_session_repos(key)
        site = self._cog_controller.load_site()

        home_site_link = ""
        cart_msg = self._cog_controller.i18n.gettext(
            'Drag & drop your links here<br>for future reference')
        reset_cart = ('<li class="placeholder rotate">{}.</li></ul>').format(
            cart_msg)
        site._cog_controller.add_json_res({
            '#cog_log_link':self.w3login_link(),
            '#cog_home_link':home_site_link,
            '#cog_session':self._cog_controller.new_session,
            '#cog_cart ul':reset_cart,
            '#cog_user_actions':'',
            '#page_ref':self._cog_controller.get_page_ref(
                'w3display', site.cog_oid_.value),
            '#cog_container':site.w3display(cog_first_call = True)})

    def __authentication(self, login, password, domain):
        if not password:
            return False
        if login.find('@') != -1:
            self.email_.value = login.strip()
        else:
            self.pseudo_.value = login.strip()
        if not self.count() <= 1: raise ToManyAccountError
        if self.count():
            self.get()
            login = self.pseudo_.value
            if self.ldap_.value is None:
                return self.__db_auth(password)
        # we check for an ldap account even if it's not yet in the db
        #XXX only if it's open bar. Some applications use ldap and have
        # restricted access to a subset of the ldap users.
        if ldap_:
            try:
                user_info, domain = self.__ldap_auth(login, password, domain)
            except:
                return False
            if user_info and self.is_empty():
                new = self.new_account(
                    pseudo_ = login,
                    first_name_ = user_info[domain['first_name_attr_']][0],
                    last_name_ = user_info[domain['last_name_attr_']][0],
                    email_ = user_info[domain['e_mail_attr_']][0].lower(),
                    ldap_ = domain['cog_oid_'])
                self.cog_oid_.value = new.cog_oid_.value
            return user_info and True

    def __db_auth(self, password):
        this = self.get()
        salted_password = "%s%s" % (this.validation_key_, password)
        c_p = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return c_p == this.password_

    def __ldap_auth(self, login, password, domain):
        return self.db.table('collorg.auth.d_ldap').auth(
            login, password, domain)

    def is_valid(self):
        return self.get().valid_account_ == True

    def valid_account(self, validation_key):
        self = self.get()
        assert self.validation_key_ == validation_key
        n_self = self()
        n_self.valid_account_.value = True
        return self.update(n_self)

    def is_member(self, data):
        return (data.members * self).count() > 0

    def has_access(self, data, write = None):
        data_oid = data.cog_oid_
        data_base = self.db.table('collorg.core.base_table')
        data_base.cog_oid_.value = data_oid
        data_env = data_base()
        access = self.db.table('collorg.access.access')
        access.user_.value = self.cog_oid_.value
        data_env.cog_oid_.value = data_base.cog_environment_
        access.data_.value = data_oid
        access.data_ += (data_env.cog_oid_, '=')
        if write: #XXX ??? Do not remove (weird)
            access.write_.value = write
        if access.is_granted():
            return True
        # if no direct access we look at the groups
        # 1 - has a group_access been defined on the checked data.
        #     Warning! we might have more than one group access defined.
        # 2 - if a group exists and self (user) has an access granted
        #     on the group, then the access is granted
        group_access = self.db.table('collorg.access.group_access')
        if write:
            group_access.write_.value = write
        group_access.accessed_data_.value = data_oid.value
        return not group_access.is_empty() and self.has_access(
            group_access._group_data_, write)

    def has_write_access(self, data):
        group = data._rev_group_access_group_data_.granted(
            write=True)._group_data_
        return self.has_access(data, True) or self.has_access(group)

    def get_granted_data(self, fqtn=None):
        data = self._rev_access_.granted()._data_
        data1 = self._rev_access_.granted()._data_
        gdata = data1._rev_group_access_group_data_.granted()._accessed_data_
        if fqtn:
            data.cog_restrict_to_type(fqtn)
            gdata.cog_restrict_to_type(fqtn)
        data += gdata
        if fqtn:
            fdata = self.db.table(fqtn)
            fdata.cog_oid_.value = data.cog_oid_
            return fdata
        return data

    def has_function(self, function_long_name):
        """
        Has the function if has a role granted...
        """
        assert self.count() == 1
        function = self.db.table(
            'collorg.actor.function', long_name_ = function_long_name)
        role = function._rev_role_
        access = self._rev_access_
        access.granted()
        role *= access._rev_role_
        return role.is_granted()

    def __wait_granted_access(self, data, timeout=2):
        from time import sleep
        delta = 0.5
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.has_access(data):
                return
            elapsed_time += delta
            sleep(delta)

    def grant_access(
        self, data, write = False, function = None,
        begin_date = None, end_date = None, pourcentage = None):
        access = self._rev_access_
        access._data_ = data
        if not access.is_granted():
            access.grant(
                self, write=write, begin_date=begin_date, end_date=end_date,
                pourcentage = pourcentage)
        if function is not None:
            role = access._rev_role_
            role._function_ = function
            if role.is_empty():
                role.insert()
        self.__wait_granted_access(data)
        return access

    def revoke_access(self, data, delete=False):
        access = self._rev_access_
        access._data_ = data
        access.revoke(delete=delete)

    def revoke_write_access(self, data):
        access = self._rev_access_
        access._data_ = data
        access.revoke_write()

    def grant_write_access(self, data):
        access = self._rev_access_
        access._data_ = data
        access.grant_write()

    def update_passwd(self, **kwargs):
        password = kwargs['old_password']
        new_password = kwargs['new_password']
        ok = self.__authentication(self.pseudo_.value, password, '')
        if ok:
            salt, enc_password = self.__encrypt_password(new_password)
            user = self()
            user.password_.value = enc_password
            user.validation_key_.value = salt
            self.update(user)
            return True
        return False

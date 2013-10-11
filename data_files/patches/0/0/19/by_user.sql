SET search_path = "collorg.communication", "collorg.communication.blog",
    "collorg.actor", "collorg.group", "collorg.access";
DROP VIEW "collorg.communication.blog.view".by_user;
CREATE VIEW "collorg.communication.blog.view".by_user AS
SELECT
post.cog_oid AS post_oid,
post.cog_creat_date AS post_creat_date,
post.cog_modif_date AS post_modif_date,
post.title AS post_title,
post.public AS public_post,
post.important AS important_post,
post.broadcast AS broadcast_post,
post.expiration_date AS expiration_date,
user_a.cog_oid AS user_a_oid,
user_o.cog_oid AS author_oid,
user_o.first_name AS author_first_name,
user_o.last_name AS author_last_name,
'[' || string_agg(atp.tag, '][' order by atp.inst_tag desc, atp.order) || ']' AS tags,
string_agg(atp.inst_tag::text, ' ' order by atp.inst_tag desc, atp.order) AS inst_tags,
pg.cog_oid AS group_oid,
pg.name AS group_name,
data.cog_oid AS data_oid
FROM
post
JOIN "group" ug ON
post.author_s_group = ug.cog_oid
JOIN "user" user_o ON
ug.data = user_o.cog_oid
JOIN "role" ON
role.data = post.cog_oid
JOIN access ON
access."role" = "role".cog_oid
JOIN "user" user_a ON
user_a.cog_oid = access.user
LEFT JOIN a_post_group apg ON
post.cog_oid = apg.post
LEFT JOIN "group" pg ON
apg."group" = pg.cog_oid
LEFT JOIN a_tag_post atp ON
post.cog_oid = atp.post
LEFT JOIN tag ON
atp.tag = tag.tag
LEFT JOIN "collorg.core".oid_table data ON
pg.data = data.cog_oid
GROUP BY
post.cog_oid, post.title, post."text",
post.important, post.broadcast, post.expiration_date,
user_a.cog_oid,
user_o.cog_oid, user_o.first_name, user_o.last_name,
pg.cog_oid, pg.name, data.cog_oid
ORDER BY
post.cog_creat_date
;

from .database_controller import DatabaseController
from collections import Counter

class TagController:
  def __init__(self, db=None, test=False):
    self.db = db if db else DatabaseController(test)
    self.image_table_columns = self.db.get_columns('Image')

  def _create(self, tag_name):
    if not self.db.exists('Tag', ('name', tag_name.lower())):
      self.db.create('Tag', {'name': tag_name.lower()})
    return self.db.find_by('Tag', ('name', tag_name.lower()))

  def tag(self, image_id, tags):
    for tag_name in tags.split(' '):
      if not self.db.exists('Image', ('id', image_id)):
        continue
      tag = self._create(tag_name)

      if self.db.exists('ImageTag', {'tag_id': tag['id'], 'image_id': image_id}):
        continue

      self.db.create('ImageTag', {'tag_id': tag['id'], 'image_id': image_id})

  def all(self, value=None):
    if type(value) == int:
      return self._all_from_image_id(value)
    elif type(value) == str:
      return self._all_from_tag_name(value)

  def remove(self, id, tag_name):
    tag_id = self.db.get_id('Tag', {'name': tag_name})

    if not tag_id:
      return

    image_tag_id = self.db.get_id('ImageTag',
                                  {'image_id': id, 'tag_id': tag_id})

    if not image_tag_id:
      return

    self.db.delete('ImageTag', ('id', image_tag_id))

    if not self.db.exists('ImageTag', {'tag_id': tag_id}):
      self.db.delete('Tag', ('id', tag_id))

  def find(self, tags):
    excluded_tags = []
    search_tags = []
    exclude_sql = ""

    for tag in filter(lambda tag: type(tag) == str and len(tag) > 1, tags):
      if tag[0] == '-':
        excluded_tags.append(tag[1:])
      else:
        search_tags.append(tag)

    if len(excluded_tags):
      exclude_sql = self.db.sql_from_lists('Tag.name', excluded_tags, 'OR')
      front = "AND I.id"  if len(search_tags) else "WHERE I.id"
      exclude_sql = f"{front} NOT IN (SELECT ImageTag.image_id\
                                      FROM ImageTag\
                                        JOIN Tag ON Tag.id=ImageTag.tag_id\
                                      WHERE {exclude_sql})"

    include_sql = " WHERE " if len(search_tags) else ""
    if len(search_tags):
      include_sql += self.db.sql_from_lists('T.name', search_tags, "OR")

    sql = f"SELECT I.{',I.'.join(self.image_table_columns)}\
            FROM Tag as T\
              JOIN ImageTag as IT ON IT.tag_id=T.id\
              JOIN Image as I ON IT.image_id=I.id\
            {include_sql}\
            {exclude_sql}\
            GROUP BY I.id\
            HAVING COUNT(*)>={len(search_tags)}"

    images = self.db.execute(sql).fetchall()
    return tuple(map(
      lambda image: dict(zip(self.image_table_columns, image)),
      images))

  def _all_from_image_id(self, id):
      tags = self.db.find_by('ImageTag', {'image_id': id}, True)
      if not tags:
        return ()
      sql = self.db.sql_from_lists('id',
                                      [tag['tag_id'] for tag in tags],
                                      "OR")
      return tuple(
        [x[0] for x in\
          self.db.execute(f"SELECT name FROM Tag WHERE {sql}").fetchall()])

  def _all_from_tag_name(self, name):
      tag_id = self.db.get_id('Tag', {'name': name})
      if not tag_id:
        return ()
      sql = f"SELECT *\
              FROM Image\
                WHERE Image.id IN (SELECT image_id\
                                   FROM ImageTag\
                                   WHERE tag_id={tag_id})"
      return tuple(
        [self.db.to_record('Image', record)\
          for record in self.db.execute(sql).fetchall()])

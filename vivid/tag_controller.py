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
      tags = self.db.find_by('ImageTag', {'image_id': value}, True)
      if not tags:
        return ()
      tag_ids = [tag['tag_id'] for tag in tags]
      return tuple([self.db.find_by(
                                    'Tag',
                                    {'id': tag_id})['name']
                      for tag_id in tag_ids])
    elif type(value) == str:
      tag = self.db.find_by('Tag', {'name': value})
      if not tag:
        return ()
      tag_id = tag['id']
      image_ids = [tag['image_id'] for tag in self.db.find_by('ImageTag',
                                                            {'tag_id': tag_id},
                                                            True)]
      return tuple([self.db.find_by('Image', {'id': img_id})
                                                      for img_id in image_ids])

  def remove(self, id, tag_name):
    tag = self.db.find_by('Tag', {'name': tag_name})

    if not tag:
      return

    tag_id = tag['id']
    image_tag = self.db.find_by('ImageTag',
                                  {'image_id': id,
                                  'tag_id': tag_id})

    if not image_tag:
      return

    self.db.delete('ImageTag', ('id', image_tag['id']))

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

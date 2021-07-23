from .database_controller import DatabaseController
from collections import Counter

class TagController:
  def __init__(self, db=None, test=False):
    self.db = db if db else DatabaseController(test)

  def _create(self, tag_name):
    if not self.db.exists('Tag', ('name', tag_name)):
      self.db.create('Tag', {'name': tag_name})
    return self.db.find_by('Tag', ('name', tag_name))

  def tag(self, image_id, tag_name):
    if not self.db.exists('Image', ('id', image_id)):
      return {}
    tag = self._create(tag_name)

    if self.db.exists('ImageTag', {'tag_id': tag['id'], 'image_id': image_id}):
      return {}

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

    for tag in filter(lambda tag: type(tag) == str and len(tag) > 1, tags):
      if tag[0] == '-':
        excluded_tags.append(tag[1:])
      else:
        search_tags.append(tag)

    images = [self.all(tag) for tag in search_tags]
    images = [x for _ in images for x in _]
    common_images = []
    most_common = Counter([x['id'] for x in images]).most_common()

    for (img_id, img_frequency) in most_common:
      if img_frequency < len(search_tags):
        break

      for image in images:
        if image['id'] == img_id:
          has_excluded = False

          for excluded_tag in excluded_tags:
            exclude_tag = self.db.find_by('Tag', {'name': excluded_tag})
            if exclude_tag and\
                self.db.find_by('ImageTag', {'tag_id': exclude_tag['id'],
                                            'image_id': image['id']}):
              has_excluded = True
              break

          if has_excluded:
            continue

          common_images.append(image)
          break

    return tuple(common_images)

import os
import imagehash
from PIL import Image
from .filesearch import get_files
from .database_controller import DatabaseController
from .blacklist import Blacklist
from os.path import isdir, isfile, exists
from pathlib import Path
from .config import Config
import random, string
import fleep
from .vivid_logger import VividLogger as Logger


class ImageController:
    blacklist = Blacklist()
    logging = Config().read("image_controller", "logging")
    logger = None

    def __init__(self, db=None, test=False, **kwargs):
        self.table_name = "Image"
        self.db = db if db else DatabaseController(test)
        if ImageController.logger is None:
            ImageController.setup_logger()
        self._create_thumbnails_path(test)
        self.use_blacklist = kwargs.get("use_blacklist", True)
        self._retrieve_blacklisted()

    def add(self, path, **kwargs):
        if isdir(path):
            self.add_directory(path, False, **kwargs)
        elif isfile(path):
            self.add_image(path, **kwargs)
        return self

    def add_image(self, path, **kwargs):
        img_hash = self._get_hash(path)
        if self._before_add_image(path=path, img_hash=img_hash, **kwargs) == -1:
            return self

        name = self._generate_name(path, img_hash, **kwargs)
        attribute_pairs = [
            ("path", path),
            ("name", name),
            ("hash", img_hash),
            self._get_image_type(path),
        ]

        record_id = self.db.create(
            self.table_name,
            dict(
                zip(
                    list(map(lambda x: x[0], attribute_pairs)),
                    list(map(lambda x: x[1], attribute_pairs)),
                )
            ),
        )
        self._create_thumbnail(path, record_id)
        self.logger.added("add_image", path, "Image")
        return self

    def add_directory(self, path, toplevel_only=True, **kwargs):
        if self.is_blacklisted((path, "directory")):
            self.logger.skip("add_directory", path, "Blacklisted directory")
            return self
        for file in get_files(path, toplevel_only):
            self.add_image(file.path, **kwargs)
        return self

    def remove(self, path, **kwargs):
        self._remove_thumbnail(path)
        should_blacklist = kwargs.get("blacklist", False)
        image_data = self.db.find_by("Image", {"path": path})
        self.logger.write(f"#remove: Removing {path} from database", 0)
        self.db.delete("Image", ("path", path))

        if should_blacklist == "hash" or should_blacklist == "all":
            self.blacklist_image(image_data["hash"], "hash")
        if should_blacklist == "path" or should_blacklist == "all":
            self.blacklist_image(image_data["path"], "path")

        if kwargs.get("db_only", True):
            return self
        if os.path.exists(path):
            os.remove(path)
        return self

    def blacklist_image(self, textable, textable_type):
        if self.db.exists("ImageBlacklist", {"textable": textable}):
            return self
        self.logger.blacklist("blacklist_image", textable_type, textable)
        self.db.create(
            "ImageBlacklist", {"textable": textable, "textable_type": textable_type}
        )
        return self

    def blacklist_directory(self, path):
        if self.db.exists("ImageBlacklist", {"textable": path}):
            return self
        self.logger.blacklist("blacklist_directory", "directory", path)
        self.db.create(
            "ImageBlackList", {"textable": path, "textable_type": "directory"}
        )
        ImageController.blacklist.add(path)
        return self

    def get_thumbnail(self, image_id):
        return f"{self.thumbnails_path}{image_id}.png"

    def rename(self, path, new_name, on_disk=True, in_db=True):
        img_data = self.db.find_by(
            "Image",
            (
                "path",
                path,
            ),
        )
        img_path = ["path", path]

        if on_disk:
            new_path = f"{os.path.split(path)[0]}/{new_name}.{img_data['image_type']}"
            ImageController.logger.rename("rename", path, new_path, "on disk")

            if os.path.exists(new_path):
                return img_path

            img_path[1] = new_path
            os.rename(path, img_path[1])
            self.db.update("Image", img_data["id"], (img_path,))

        if in_db:
            ImageController.logger.rename("rename", path, new_path, "in database")
            self.db.update(
                "Image",
                img_data["id"],
                (
                    (
                        "name",
                        new_name,
                    ),
                ),
            )

        return tuple(img_path)

    def existence_check(self):
        for image in self._each_image():
            path = image["path"]
            if not exists(path):
                self.logger.write(
                    f"#existance_check: Removing thumbnail belong to id={image['id']} and path={path}",
                    0,
                )
                self.remove(path, db_only=True)

    def is_blacklisted(self, data=()):
        if not self.use_blacklist:
            return False

        (textable, textable_type) = data
        if textable_type == "path" or textable_type == "directory":
            if ImageController.blacklist.exists(textable):
                return True
            if textable_type == "directory":
                return False

        return not not self.db.find_by(
            "ImageBlacklist", {"textable": textable, "textable_type": textable_type}
        )

    def recreate_thumbnails(self):
        for image in self._each_image():
            try:
                self._create_thumbnail(image["path"], image["id"])
            except Exception as e:
                print(e)

    def update_metadata(self, img_ids, metadata):
        if type(img_ids) != list:
            img_ids = [img_ids]
        self.logger.write(
            f"#update_metadata: Updating images with id('s)={img_ids} to value('s)={list(metadata.items())}",
            0,
        )
        for img_id in img_ids:
            self.db.update(
                "Image",
                img_id,
                [(attribute, value) for attribute, value in metadata.items()],
            )

    @classmethod
    def read_config(cls):
        ImageController.logging = Config().read("image_controller", "logging")

    def _before_add_image(self, **kwargs):
        blacklist_check = kwargs.get("blacklist_check", True)
        path = kwargs["path"]
        img_hash = kwargs["img_hash"]

        if blacklist_check:
            if self.is_blacklisted((img_hash, "hash")):
                self.logger.skip("add_image", path, "Blacklisted path")
                return -1
            if self.is_blacklisted((path, "path")):
                self.logger.skip(
                    "add_image", path, "Blacklisted path or directory ancestor"
                )
                return -1
        if not self._is_valid(**kwargs):
            self.logger.skip("add_image", path, "Image is invalid or already exists")
            return -1

    def _get_image_type(self, path):
        with open(path, "rb") as file:
            info = fleep.get(file.read(128))
        if len(info.type) != 0 and info.type[0].find("image") != -1:
            return ("image_type", info.extension[0])
        else:
            return ("image_type", "")

    def _get_hash(self, path):
        try:
            h = imagehash.phash(Image.open(path))
        except Exception as e:
            print(e)
        else:
            return str(h)

    def _each_image(self):
        for image in self.db.between(
            "Image", self.db.get_first("Image")["id"], self.db.get_last("Image")["id"]
        ):
            yield image

    def _create_thumbnail(self, path, image_id):
        with Image.open(path) as img:
            img.thumbnail(
                (
                    250,
                    125,
                )
            )
            img.save(Path(f"{self.thumbnails_path + str(image_id)}.png"), format="PNG")

    def _retrieve_blacklisted(self):
        if not self.use_blacklist:
            return

        sql = f"SELECT textable AS directories\
            FROM ImageBlacklist\
            WHERE textable_type='directory'"
        for x in self.db.execute(sql).fetchall():
            ImageController.blacklist.add(x[0])

    def _remove_thumbnail(self, path):
        data = self.db.find_by("Image", ("path", path))
        if not data:
            return
        img_id = data["id"]
        thumbnail_path = f"{self.thumbnails_path + str(img_id)}.png"
        if isfile(thumbnail_path):
            os.remove(thumbnail_path)

    def _create_thumbnails_path(self, test):
        self.thumbnails_path = "./tests/thumbnails" if test else "./thumbnails"
        if not isdir(self.thumbnails_path):
            os.mkdir(self.thumbnails_path)
        self.thumbnails_path += "/"

    def _is_valid(self, path, img_hash, **kwargs):
        if (
            self.db.exists("Image", ("path", path))
            or not img_hash
            or (
                kwargs.get("unique", False)
                and self.db.exists("Image", ("hash", img_hash))
            )
        ):
            return False
        return True

    def _generate_name(self, path, img_hash, **kwargs):
        if kwargs.get("scramble_name", False):
            return self._random_string(32)
        elif kwargs.get("hash_as_name", False):
            return img_hash
        return os.path.splitext(os.path.basename(path))[0]

    def _random_string(self, length):
        return "".join(random.choice(string.ascii_lowercase) for i in range(length))

    @classmethod
    def setup_logger(self):
        ImageController.logger = Logger("Image Controller")
        ImageController.logger.register(
            "skip", "#%s: Skipping %s | Reason: %s", level=0
        )
        ImageController.logger.register("added", "#%s: Added %s to %s table", level=0)
        ImageController.logger.register("blacklist", "#%s: Blacklisting %s %s", level=0)
        ImageController.logger.register("rename", "#%s: Renaming %s to %s %s", level=0)

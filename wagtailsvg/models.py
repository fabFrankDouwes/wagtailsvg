import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from wagtail.search import index

from wagtailsvg.signals import svg_saved

try:
    from wagtail.models import CollectionMember
    from wagtail.admin.panels import TabbedInterface
    from wagtail.admin.panels import ObjectList
    from wagtail.admin.panels import FieldPanel
except ImportError:
    from wagtail.core.models import CollectionMember
    from wagtail.admin.edit_handlers import TabbedInterface
    from wagtail.admin.edit_handlers import ObjectList
    from wagtail.admin.edit_handlers import FieldPanel

from taggit.managers import TaggableManager


def get_svg_upload_to_folder(instance, filename):
    folder = settings.WAGTAILSVG_UPLOAD_FOLDER or 'media'
    return os.path.join(folder, filename)


class Svg(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    file = models.FileField(
        upload_to=get_svg_upload_to_folder,
        verbose_name=_("file")
    )
    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    class Meta:
        ordering = ['-id']

    admin_form_fields = (
        "title",
        "file",
        "collection",
        "tags",
    )

    edit_handler = TabbedInterface([
        ObjectList([
            FieldPanel('collection'),
            FieldPanel('title'),
            FieldPanel('file'),
            FieldPanel('tags'),
        ], heading="General"),
    ])

    def __str__(self):
        return self.title

    # check where this page has been used
    def get_usage(self):
        return ReferenceIndex.get_references_to(self).group_by_source_object()
    
    def save(self, force_insert=False, force_update=False, using=None,
         update_fields=None):


    super().save(force_insert=force_insert, force_update=force_update, using=using,
                 update_fields=update_fields)

    # send a signal to bust all cache
    svg_saved.send(sender=self.__class__, instance=self)
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def url(self):
        return self.file.url

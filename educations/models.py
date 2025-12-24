from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator

from django_countries.fields import CountryField


class Speciality(models.Model):
    code = models.CharField(
        default="053", max_length=3,
        validators=[MinLengthValidator(3)]
    )
    title = models.CharField(
        max_length=128, default="Psychology"
    )
    code_world = models.CharField(
        default="0313", max_length=4,
        validators=[MinLengthValidator(4)]
    )
    title_world = models.CharField(
        max_length=128, default="Psychology"
    )
    is_medical = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Speciality')
        verbose_name_plural = _('Specialities')

    def __str__(self):
        return f'{self.code} {self.title}'


class University(models.Model):
    title = models.CharField(max_length=128, default="")
    title_world = models.CharField(max_length=128, default="")
    country = CountryField(blank_label="(Select country)")

    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')

    def __str__(self):
        return str(self.title)


# TODO: possibility to upload or share a diploma or a certificate
class Education(models.Model):
    class DegreeChoices(models.IntegerChoices):
        COURSE = 0, _("Course")
        UNDER = 1, _("Undergraduate")
        SPEC = 2, _("Specialist")
        MASTER = 3, _("Master")
        POST = 4, _("Postgraduate")
        DOC = 5, _("Doctor")

    university = models.ForeignKey(University, on_delete=models.PROTECT)
    degree = models.SmallIntegerField(choices=DegreeChoices.choices, default=DegreeChoices.COURSE)
    speciality = models.ForeignKey('Speciality', on_delete=models.PROTECT, null=True)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return f'{self.get_degree_display()}, {self.speciality}, {self.university} ({self.date_start} - {self.date_end})'

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    @property
    async def education_duration(self):
        delta = self.date_start - self.date_end
        return round(delta.days / 365)

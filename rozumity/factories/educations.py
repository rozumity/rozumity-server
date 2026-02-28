
import factory
from datetime import date, timedelta

from educations.models import Speciality, University, Education


from .base import Factory

# --- EDUCATIONS FACTORIES ---

class SpecialityFactory(Factory):
    class Meta:
        model = Speciality

    code = factory.Iterator(["053", "035", "225"])
    title = factory.Iterator(["Psychology", "Philology", "Medical Psychology"])
    code_world = "0313"
    title_world = "Psychology"
    is_medical = False


class UniversityFactory(Factory):
    class Meta:
        model = University

    title = factory.Sequence(lambda n: f"University of Technology №{n}")
    title_world = factory.Sequence(lambda n: f"University of Technology №{n}")
    country = "US"


class EducationFactory(Factory):
    class Meta:
        model = Education

    university = factory.SubFactory(UniversityFactory)
    degree = Education.DegreeChoices.MASTER
    speciality = factory.SubFactory(SpecialityFactory)
    date_start = factory.LazyFunction(lambda: date.today() - timedelta(days=5*365))
    date_end = factory.LazyFunction(lambda: date.today() - timedelta(days=1*365))

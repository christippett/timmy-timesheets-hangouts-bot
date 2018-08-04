from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


class Space(Model):
    class Meta:
        table_name = 'team2-space'
        region = 'ap-southeast-2'
    name = UnicodeAttribute(hash_key=True)
    type = UnicodeAttribute(null=False)
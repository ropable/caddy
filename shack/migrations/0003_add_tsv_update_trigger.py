# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-22 03:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shack', '0002_add_tsvector_column'),
    ]

    operations = [
        migrations.RunSQL('''CREATE FUNCTION shack_address_search_trigger() RETURNS trigger AS $$
begin
  new.tsv :=
    setweight(to_tsvector(coalesce(new.data->>'road','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'locality','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'survey_lot','')), 'B') ||
    setweight(to_tsvector(coalesce(new.address_text,'')), 'D');
  return new;
end
$$ LANGUAGE plpgsql;'''),
        migrations.RunSQL('DROP TRIGGER IF EXISTS shack_address_tsv_update ON shack_address;'),
        migrations.RunSQL('''CREATE TRIGGER shack_address_tsv_update BEFORE INSERT OR UPDATE
ON shack_address FOR EACH ROW EXECUTE PROCEDURE shack_address_search_trigger();'''),
    ]
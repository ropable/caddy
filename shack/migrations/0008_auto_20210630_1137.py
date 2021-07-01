# Generated by Django 3.2.3 on 2021-06-30 03:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shack', '0007_alter_address_data'),
    ]

    operations = [
        migrations.RunSQL('''CREATE OR REPLACE FUNCTION shack_address_search_trigger() RETURNS trigger AS $$
begin
  new.tsv :=
    setweight(to_tsvector(coalesce(new.data->>'road_name','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'locality','')), 'A') ||
    setweight(to_tsvector(coalesce(new.data->>'lot_number','')), 'B') ||
    setweight(to_tsvector(coalesce(new.data->>'pin','')), 'B') ||
    setweight(to_tsvector(coalesce(new.address_text,'')), 'D');
  return new;
end
$$ LANGUAGE plpgsql;'''),
    ]
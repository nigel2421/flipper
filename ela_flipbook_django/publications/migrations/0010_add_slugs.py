from django.db import migrations, models
from django.utils.text import slugify


def generate_slug(model_class, title, pk):
    base_slug = slugify(title) or f"item-{pk}"
    slug = base_slug
    counter = 1
    while model_class.objects.filter(slug=slug).exclude(pk=pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def populate_magazine_slugs(apps, schema_editor):
    Magazine = apps.get_model('publications', 'Magazine')
    for obj in Magazine.objects.filter(slug__isnull=True):
        obj.slug = generate_slug(Magazine, obj.title, obj.pk)
        obj.save(update_fields=['slug'])


def populate_article_slugs(apps, schema_editor):
    Article = apps.get_model('publications', 'Article')
    for obj in Article.objects.filter(slug__isnull=True):
        obj.slug = generate_slug(Article, obj.title, obj.pk)
        obj.save(update_fields=['slug'])


def populate_whatsapp_slugs(apps, schema_editor):
    WhatsAppUpdate = apps.get_model('publications', 'WhatsAppUpdate')
    for obj in WhatsAppUpdate.objects.filter(slug__isnull=True):
        obj.slug = generate_slug(WhatsAppUpdate, obj.title, obj.pk)
        obj.save(update_fields=['slug'])


def add_slug_columns_safe(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    print(f"\n[MIGRATION] Detected database vendor: {vendor}")
    
    tables = ['publications_magazine', 'publications_article', 'publications_whatsappupdate']
    
    if vendor == 'postgresql':
        print(f"[MIGRATION] Running PostgreSQL-specific safe column addition...")
        for table in tables:
            schema_editor.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='{table}' AND column_name='slug'
                    ) THEN
                        ALTER TABLE {table} ADD COLUMN slug varchar(220) NULL;
                    END IF;
                END $$;
            """)
    elif vendor == 'sqlite':
        print(f"[MIGRATION] Running SQLite-specific safe column addition...")
        for table in tables:
            # Check if column exists in SQLite
            cursor = schema_editor.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [c[1] for c in cursor.fetchall()]
            if 'slug' not in columns:
                schema_editor.execute(f"ALTER TABLE {table} ADD COLUMN slug varchar(220) NULL;")
    elif vendor == 'mysql':
        print(f"[MIGRATION] Running MySQL-specific safe column addition...")
        for table in tables:
            cursor = schema_editor.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '{table}' AND column_name = 'slug';")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN slug varchar(220) NULL;")
    else:
        print(f"[MIGRATION] Vendor {vendor} not specifically handled, skipping raw SQL column addition.")

def create_unique_indexes_safe(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        print(f"[MIGRATION] Creating unique indexes (PostgreSQL)...")
        schema_editor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS publications_magazine_slug_unique
                ON publications_magazine (slug) WHERE slug IS NOT NULL;
            CREATE UNIQUE INDEX IF NOT EXISTS publications_article_slug_unique
                ON publications_article (slug) WHERE slug IS NOT NULL;
            CREATE UNIQUE INDEX IF NOT EXISTS publications_whatsappupdate_slug_unique
                ON publications_whatsappupdate (slug) WHERE slug IS NOT NULL;
        """)
    elif vendor == 'sqlite':
        print(f"[MIGRATION] Creating unique indexes (SQLite)...")
        # SQLite IF NOT EXISTS for indexes
        schema_editor.execute("CREATE UNIQUE INDEX IF NOT EXISTS publications_magazine_slug_unique ON publications_magazine (slug);")
        schema_editor.execute("CREATE UNIQUE INDEX IF NOT EXISTS publications_article_slug_unique ON publications_article (slug);")
        schema_editor.execute("CREATE UNIQUE INDEX IF NOT EXISTS publications_whatsappupdate_slug_unique ON publications_whatsappupdate (slug);")
    elif vendor == 'mysql':
        print(f"[MIGRATION] Creating unique indexes (MySQL)...")
        tables = ['publications_magazine', 'publications_article', 'publications_whatsappupdate']
        for table in tables:
            cursor = schema_editor.connection.cursor()
            idx_name = f"{table}_slug_unique"
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = '{table}' AND index_name = '{idx_name}';")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"CREATE UNIQUE INDEX {idx_name} ON {table} (slug);")

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('publications', '0009_alter_magazine_pdf_file'),
    ]

    operations = [
        # Step 1: Add slug columns safely
        migrations.RunPython(add_slug_columns_safe, migrations.RunPython.noop),

        # Step 2: Tell Django's migration state about the fields
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='magazine',
                    name='slug',
                    field=models.SlugField(max_length=220, null=True, blank=True),
                ),
                migrations.AddField(
                    model_name='article',
                    name='slug',
                    field=models.SlugField(max_length=220, null=True, blank=True),
                ),
                migrations.AddField(
                    model_name='whatsappupdate',
                    name='slug',
                    field=models.SlugField(max_length=220, null=True, blank=True),
                ),
            ],
        ),

        # Step 3: Populate slugs for all existing records
        migrations.RunPython(populate_magazine_slugs, migrations.RunPython.noop),
        migrations.RunPython(populate_article_slugs, migrations.RunPython.noop),
        migrations.RunPython(populate_whatsapp_slugs, migrations.RunPython.noop),

        # Step 4: Add unique index safely
        migrations.RunPython(create_unique_indexes_safe, migrations.RunPython.noop),

        # Step 5: Update Django state to reflect the unique constraint
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='magazine',
                    name='slug',
                    field=models.SlugField(max_length=220, unique=True, blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='article',
                    name='slug',
                    field=models.SlugField(max_length=220, unique=True, blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='whatsappupdate',
                    name='slug',
                    field=models.SlugField(max_length=220, unique=True, blank=True, null=True),
                ),
            ],
        ),
    ]

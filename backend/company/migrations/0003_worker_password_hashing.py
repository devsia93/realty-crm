"""Hand-written migration: reconcile Worker.password with AbstractUser (task 050).

Background
----------
``Worker`` overrode ``AbstractUser.password`` with a plain
``CharField(max_length=255, verbose_name='Пароль')`` — a PLAINTEXT shadow of
Django's hashed field. That override has been deleted on the model, so
AbstractUser's hashed-password machinery (``set_password`` / ``check_password``
/ ``make_password``) now owns the column.

Why hand-written (not ``makemigrations``)
-----------------------------------------
The autodetector would emit ``RemoveField`` for the dropped override — which is
WRONG: it would DROP the ``password`` column that AbstractUser still needs.
Instead we:

  1. (data) hash any existing plaintext rows in place with ``make_password`` so
     no account is locked out and no plaintext survives the cut-over;
  2. (schema) ``AlterField`` the column back to AbstractUser's definition:
     ``CharField(max_length=128, verbose_name='password')``.

Order matters: hashing runs while the column is still ``max_length=255`` (so even
over-long legacy plaintexts fit), THEN the column is narrowed to 128 (a hashed
value is ~78 chars). On a fresh dev DB there are no rows, so step 1 is a no-op;
the migration is nevertheless written to be correct on a populated DB.

Reverse is a no-op: a hash cannot be un-hashed, and we never restore plaintext.
"""
from django.db import migrations, models


# Recognized Django hasher prefixes — used to skip rows that are already hashed
# so a re-application (or partially-historical DB) never double-hashes and locks
# accounts out. '!' is Django's UNUSABLE_PASSWORD_PREFIX.
_HASHED_PREFIXES = (
    'pbkdf2_',
    'argon2',
    'bcrypt$',
    'bcrypt_sha2$',
    'sha1$',
    'md5$',
    'crypt$',
    'scrypt$',
    '!',
)


def hash_plaintext_passwords(apps, schema_editor):
    from django.contrib.auth.hashers import make_password

    Worker = apps.get_model('company', 'Worker')
    for worker in Worker.objects.iterator():
        if worker.password.startswith(_HASHED_PREFIXES):
            continue
        worker.password = make_password(worker.password)
        worker.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20260709_2216'),
    ]

    operations = [
        migrations.RunPython(hash_plaintext_passwords, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='worker',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]

#!/bin/bash
cd /home/natalia_jimnez/envxv/invitaciondigital
../bin/python manage.py createsuperuser --noinput --username admin --email admin@example.com || true
../bin/python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); u.set_password('admin123'); u.save()"
chmod 666 db.sqlite3

#!/usr/bin/env bash

# Environment variables may not be loaded under all conditions.
if [ -z "${TWLIGHT_HOME}" ]
then
    source /etc/environment
fi

source ${TWLIGHT_HOME}/bin/virtualenv_activate.sh

echo "test --noinput"
DJANGO_SETTINGS_MODULE=TWLight.settings.local python manage.py test --noinput

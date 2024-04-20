from config_reader import config


def init_django():
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[
            'database',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config.postgres_db.get_secret_value(),
                'USER': config.postgres_user.get_secret_value(),
                'PASSWORD': config.postgres_password.get_secret_value(),
                'HOST': config.postgres_host.get_secret_value(),
                'PORT': config.postgres_port.get_secret_value(),
            }
        }
    )
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    init_django()
    execute_from_command_line()

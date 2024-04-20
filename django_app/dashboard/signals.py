# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mailing
import redis
from .config_reader import config
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Mailing)
def publish_mailing_to_redis(sender, instance, created, **kwargs):
    if created:
        try:
            # Connect to Redis
            # redis_url = f'redis://{config.redis_host.get_secret_value()}:{config.redis_port.get_secret_value()}'
            r = redis.Redis(host=config.redis_host.get_secret_value(), port=config.redis_port.get_secret_value(),
                                db=0)

            # Publish mailing.id to the Redis channel
            channel_name = 'mailings'
            r.publish(channel_name, str(instance.id))
            logger.info(f"Published mailing id {instance.id} to Redis channel {channel_name}")
        except Exception as e:
            logger.error(f"Error publishing mailing id to Redis: {e}")
        finally:
            if 'redis' in locals():
                r.close()

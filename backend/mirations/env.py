import os, sys
from logging.config import fileConfig
import time
from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api', 'src'))

from api.core.env import env
from api.db.base import Base
from api.db import models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+mysqlconnector://{env.DB_USER}:{env.DB_PASS}"
    f"@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise RuntimeError("sqlalchemy.url is not set in alembic config")
    connectable = create_engine(url, poolclass=pool.NullPool)

    retries = env.DB_RETRIES
    delay = env.DB_RETRY_DELAY
    for i in range(retries):
        try:
            with connectable.connect() as connection:
                context.configure(connection=connection, target_metadata=target_metadata)
                with context.begin_transaction():
                    context.run_migrations()
            return
        except Exception as e:
            if i < retries - 1:
                print(f"INFO:   DB not ready for migrations, retrying ({i + 1}/{retries})...")
                time.sleep(delay)
            else:
                raise Exception("Could not connect to DB for migrations after retries") from e
            
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
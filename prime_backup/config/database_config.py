from mcdreforged.api.utils import Serializable

from prime_backup.types.units import Duration


class CompactDatabaseConfig(Serializable):
	enabled: bool = True
	interval: Duration = Duration('1d')
	jitter: Duration = Duration('5m')


class DatabaseConfig(Serializable):
	compact: CompactDatabaseConfig = CompactDatabaseConfig()

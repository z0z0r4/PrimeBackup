from prime_backup.action import Action
from prime_backup.db.access import DbAccess
from prime_backup.types.backup_info import BackupInfo
from prime_backup.utils import misc_utils


class GetBackupAction(Action[BackupInfo]):
	def __init__(self, backup_id: int, calc_size: bool = True):
		super().__init__()
		self.calc_size = calc_size
		self.backup_id = misc_utils.ensure_type(backup_id, int)

	def run(self) -> BackupInfo:
		with DbAccess.open_session() as session:
			backup = session.get_backup(self.backup_id)
			return BackupInfo.of(backup, calc_size=self.calc_size)

import time
from pathlib import Path
from typing import Any, Union

from mcdreforged.api.all import *

from prime_backup import constants
from prime_backup.types.backup_info import BackupInfo
from prime_backup.types.blob_info import BlobListSummary
from prime_backup.types.operator import Operator
from prime_backup.types.units import ByteCount, Duration
from prime_backup.utils.mcdr_utils import mkcmd, click_and_run


class TextComponents:
	@classmethod
	def tr(cls, key, *args, **kwargs):
		from prime_backup.utils.mcdr_utils import tr
		return tr('text_components.' + key, *args, **kwargs)

	@classmethod
	def number(cls, value: Any) -> RTextBase:
		return RText(value, RColor.yellow)

	@classmethod
	def percent(cls, value: float, total: float) -> RTextBase:
		if total != 0:
			return RText(f'{100 * value / total:.1f}%', RColor.blue)
		else:
			return RText('N/A', RColor.gray)

	@classmethod
	def title(cls, text: Any):
		return RTextList(RText('======== ', RColor.gray), text, RText(' ========', RColor.gray))

	@classmethod
	def file_size(cls, byte_cnt: int, *, ndigits: int = 2) -> RTextBase:
		return RText(ByteCount(byte_cnt).auto_str(ndigits=ndigits), color=RColor.dark_green)

	@classmethod
	def dual_size_hover(cls, raw_size: int, stored_size: int, *, ndigits: int = 2) -> RTextBase:
		t_raw_size = cls.file_size(raw_size, ndigits=ndigits)
		t_stored_size = cls.file_size(stored_size, ndigits=ndigits)
		t_percent = cls.percent(stored_size, raw_size)
		return cls.tr('dual_size_hover', t_stored_size, t_percent, t_raw_size)

	@classmethod
	def file(cls, file_path: Path) -> RTextBase:
		return RText(file_path.name, RColor.dark_aqua).h(str(file_path.as_posix()))

	@classmethod
	def backup_id(cls, backup_id: int, *, hover: bool = True, click: bool = True) -> RTextBase:
		text = RText(f'#{backup_id}', RColor.gold)
		if hover:
			text.h(cls.tr('backup_id.hover', RText(backup_id, RColor.gold)))
		if click:
			text.c(RAction.run_command, mkcmd(f'show {backup_id}'))
		return text

	@classmethod
	def backup_comment(cls, comment: str) -> RTextBase:
		return RText(comment) if len(comment) > 0 else cls.tr('backup_comment.none').set_color(RColor.gray).set_styles(RStyle.italic)

	@classmethod
	def backup_size(cls, backup_or_blob_list_summary: Union[BackupInfo, BlobListSummary], *, ndigits: int = 2) -> RTextBase:
		b = backup_or_blob_list_summary
		return cls.file_size(b.raw_size, ndigits=ndigits).h(cls.dual_size_hover(b.raw_size, b.stored_size))

	@classmethod
	def backup_date(cls, backup: BackupInfo):
		time_since_now_sec = time.time() - backup.timestamp_ns / 1e9
		return RText(backup.date, RColor.aqua).h(cls.tr('backup_full.time_since_now', cls.duration(time_since_now_sec)))

	@classmethod
	def backup_brief(cls, backup: BackupInfo, *, backup_id_fancy: bool = True) -> RTextBase:
		# "backup #1: foobar"
		return RTextList(cls.tr(
			'backup_brief',
			cls.backup_id(backup.id, hover=backup_id_fancy, click=backup_id_fancy),
			cls.backup_comment(backup.comment),
		))

	@classmethod
	def backup_full(cls, backup: BackupInfo, operation_buttons: bool = False) -> RTextBase:
		# "[#1] [>] [x] 1.2GiB 2023-11-30 09:30:13: foobar"
		t_bid = cls.backup_id(backup.id)

		rtl = RTextList(RText('[', RColor.gray), t_bid, RText('] ', RColor.gray))
		if operation_buttons:
			rtl.append(
				RText('[>]', color=RColor.green).h(cls.tr('backup_full.restore', t_bid)).c(RAction.suggest_command, mkcmd(f'back {backup.id}')), ' ',
				RText('[x]', color=RColor.red).h(cls.tr('backup_full.delete', t_bid)).c(RAction.suggest_command, mkcmd(f'delete {backup.id}')), ' ',
			)
		rtl.append(
			cls.backup_size(backup), ' ',
			cls.backup_date(backup), RText(': ', RColor.gray),
			cls.backup_comment(backup.comment).h(cls.tr('backup_full.author', cls.operator(backup.author))),
		)
		return rtl

	@classmethod
	def command(cls, s: str, *, color: RColor = RColor.gray, suggest: bool = False, run: bool = False, raw: bool = False) -> RTextBase:
		cmd = s if raw else mkcmd(s)
		text = RText(cmd, color)
		if suggest:
			text.h(cls.tr('command.suggest', cmd)).c(RAction.suggest_command, cmd)
		elif run:
			text.h(cls.tr('command.run', cmd)).c(RAction.run_command, cmd)
		return text

	@classmethod
	def operator(cls, op: Operator) -> RTextBase:
		tr_key = f'operator.{op.type}'
		if op.type in ['player', 'command_source', 'unknown']:
			return cls.tr(tr_key, op.name)
		elif op.type in ['console', constants.PLUGIN_ID]:
			return cls.tr(tr_key)
		else:
			return RText(f'{op.type}:{op.name}')

	@classmethod
	def duration(cls, seconds: float, *, ndigits: int = 2) -> RTextBase:
		value, unit = Duration(seconds).auto_format()
		return cls.tr('duration.text', round(value, ndigits), cls.tr('duration.' + unit))

	@classmethod
	def confirm_hint(cls, what: RTextBase, time_wait_text: Any):
		return cls.tr(
			'confirm_hint.base',
			time_wait_text,
			click_and_run(
				cls.tr('confirm_hint.confirm', what).set_color(RColor.red),
				cls.tr('confirm_hint.confirm.hover', cls.command('confirm'), what),
				mkcmd('confirm'),
			),
			click_and_run(
				cls.tr('confirm_hint.abort', what).set_color(RColor.yellow),
				cls.tr('confirm_hint.abort.hover', cls.command('abort'), what),
				mkcmd('abort'),
			),
		)

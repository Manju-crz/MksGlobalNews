import os

from moviepy import AudioFileClip


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_AUDIOS_FOLDER = os.path.join(PROJECT_ROOT, "dumps", "generated_audios")


def get_audio_durations(base_filename):
	"""Return formatted durations for generated audio files matching a JSON stem."""
	base_name = os.path.splitext(os.path.basename(base_filename))[0]
	audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".wma"}
	audio_durations = {}

	if not os.path.isdir(GENERATED_AUDIOS_FOLDER):
		return audio_durations

	for file_name in sorted(os.listdir(GENERATED_AUDIOS_FOLDER)):
		file_path = os.path.join(GENERATED_AUDIOS_FOLDER, file_name)
		extension = os.path.splitext(file_name)[1].lower()
		if not file_name.startswith(base_name) or extension not in audio_extensions:
			continue
		try:
			audio_clip = AudioFileClip(file_path)
			try:
				total_seconds = round(audio_clip.duration)
				minutes, seconds = divmod(total_seconds, 60)
				audio_durations[file_name] = f"{minutes}.{seconds:02d}"
			finally:
				audio_clip.close()
		except Exception as error:
			print(f"Could not read duration for {file_name}: {error}")

	return audio_durations


def duration_to_seconds(duration):
	"""Convert a minutes.seconds duration string into total seconds."""
	minutes, seconds = duration.split(".")
	return int(minutes) * 60 + int(seconds)


def format_duration(total_seconds):
	"""Format total seconds as minutes.seconds."""
	minutes, seconds = divmod(total_seconds, 60)
	return f"{minutes}.{seconds:02d}"


def pack_audio_files(audio_files, max_seconds):
	"""Pack files into the smallest available groups without exceeding a limit."""
	packed_groups = []
	sorted_files = sorted(
		audio_files.items(),
		key=lambda item: duration_to_seconds(item[1]),
		reverse=True,
	)

	for file_name, duration in sorted_files:
		file_duration = duration_to_seconds(duration)
		candidate_index = None
		smallest_remaining = None

		for index, (_, group_duration) in enumerate(packed_groups):
			remaining = max_seconds - (group_duration + file_duration)
			if remaining >= 0 and (
				smallest_remaining is None or remaining < smallest_remaining
			):
				candidate_index = index
				smallest_remaining = remaining

		if candidate_index is None:
			packed_groups.append(({file_name: duration}, file_duration))
		else:
			group_files, group_duration = packed_groups[candidate_index]
			group_files[file_name] = duration
			packed_groups[candidate_index] = (
				group_files,
				group_duration + file_duration,
			)

	return packed_groups


def group_audio_files_by_duration(audio_durations, min_minutes=10, max_minutes=15):
	"""Group audio files into groups whose totals are between 10 and 15 minutes."""
	minimum_seconds = min_minutes * 60
	maximum_seconds = max_minutes * 60
	groups = []
	ungrouped_files = {}

	for group_files, group_duration in pack_audio_files(
		audio_durations, maximum_seconds
	):
		if group_duration >= minimum_seconds:
			groups.append((group_files, group_duration))
		else:
			ungrouped_files.update(group_files)

	return groups, ungrouped_files


def resolve_ungrouped_audio_files(groups, ungrouped_files):
	"""Repack leftovers so every possible group remains within the duration limit."""
	if not ungrouped_files:
		return groups

	ungrouped_duration = sum(
		duration_to_seconds(duration) for duration in ungrouped_files.values()
	)
	print(f"Ungrouped duration: {format_duration(ungrouped_duration)}")

	if ungrouped_duration < 5 * 60:
		if not groups:
			groups.append(({}, 0))
		group_files, group_duration = groups[0]
		group_files.update(ungrouped_files)
		groups[0] = (group_files, group_duration + ungrouped_duration)
		return groups

	packed_groups = pack_audio_files(ungrouped_files, 15 * 60)
	for packed_group, packed_duration in packed_groups:
		if packed_duration >= 10 * 60:
			groups.append((packed_group, packed_duration))
			continue

		if groups:
			group_files, group_duration = groups[0]
			group_files.update(packed_group)
			groups[0] = (group_files, group_duration + packed_duration)
		else:
			groups.append((packed_group, packed_duration))

	return groups

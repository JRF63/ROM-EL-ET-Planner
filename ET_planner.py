import roguard_et_parser

MAX_HOPS = 100

def et_scorer(et_data, mvp_targets, avoid_mvp,
			  mini_targets, extra_mini):
	scored_data = {}
	for floor, mobs_dict in et_data.items():
		is_mvp_floor = (floor % 10 == 0)
		
		for channel, mobs in mobs_dict.items():
			score = 0
			if is_mvp_floor:
				for mob in mobs:
					if mob in mvp_targets:
						score += 10
					elif mob in avoid_mvp:
						score -= 10
			else:
				for mob in mobs:
					if mob in mini_targets:
						score += 10
					elif mob in extra_mini:
						score += 1
			if floor not in scored_data:
				scored_data[floor] = {}
			scored_data[floor][channel] = score

	return scored_data

def filter_channels(scored_data):
	allowed_channels = {}

	for floor, channel_dict in scored_data.items():
		best_score = -MAX_HOPS
		best_channels = []
		for channel, score in channel_dict.items():
			if score > best_score:
				best_score = score
				best_channels = [channel]
			elif score == best_score:
				best_channels.append(channel)
		allowed_channels[floor] = best_channels

	return allowed_channels

def plan_channels(scored_data):

	allowed_channels = filter_channels(scored_data)

	floors = sorted(allowed_channels)
	max_idx = len(floors) - 1
	
	least_hops = MAX_HOPS
	best_path = []

	traversed_channels = []

	def traverse(hops, idx, channel):
		nonlocal least_hops
		nonlocal best_path

		if idx > max_idx:
			if hops < least_hops:
				least_hops = hops
				best_path = traversed_channels[:]
			return
		for next_channel in allowed_channels[floors[idx]]:
			next_hops = hops
			if (next_channel != channel) and (channel != -1):
				next_hops = hops + 1

			if next_hops > least_hops:
				continue

			traversed_channels.append(next_channel)
			traverse(next_hops, idx + 1, next_channel)
			traversed_channels.pop()

	traverse(0, 0, -1)
	return least_hops, best_path

def build_score_matrix(allowed_channels):
		score_matrix = {}
		for floor, channels in allowed_channels.items():
			score_matrix[floor] = {chan: 0 for chan in channels}
		return score_matrix

def get_last_channel(score_matrix, last_floor):
	min_hops = MAX_HOPS
	last_channel = -1
	for channel, hops in score_matrix[last_floor].items():
		if hops < min_hops:
			min_hops = hops
			last_channel = channel
	return min_hops, last_channel

def backtrack_path(backtrack_matrix, floors, last_channel):
	
	traversed_channels = []

	last_floor = floors[-1]
	channel = last_channel
	idx = len(floors) - 1
	floor = floors[idx]
	while idx > -1:
		traversed_channels.append(channel)
		channel = backtrack_matrix[floor][channel]
		idx -= 1
		floor = floors[idx]

	traversed_channels.reverse()
	
	return traversed_channels

def build_matrices(allowed_channels, floors, channels):

	score_matrix = build_score_matrix(allowed_channels)

	backtrack_matrix = {}
	for floor in allowed_channels[floors[0]]:
		backtrack_matrix[floor] = {chan: -1 for chan in channels}

	prev_floor = floors[0]
	for curr_floor in floors[1:]:
		prev_column = score_matrix[prev_floor]
		curr_column = score_matrix[curr_floor]
		trav_channel = {}
		
		for channel in curr_column:
			least_hops = MAX_HOPS
			best_prev_chan = -1
			for prev_channel, prev_score in prev_column.items():

				total = prev_score
				# if not same channel as previous, add one
				if prev_channel != channel:
					total += 1

				if total < least_hops:
					least_hops = total
					best_prev_chan = prev_channel

			curr_column[channel] = least_hops
			trav_channel[channel] = best_prev_chan
			
		prev_floor = curr_floor
		backtrack_matrix[curr_floor] = trav_channel

	min_hops, last_channel = get_last_channel(score_matrix, floors[-1])
	
	traversed_channels = backtrack_path(backtrack_matrix, floors, last_channel)

	return score_matrix, backtrack_matrix

def plan_channels2(scored_data):
	# implments dynamic programming to find the
	# path with least number of channel hops

	allowed_channels = filter_channels(scored_data)
	floors = sorted(scored_data)

	channels_dict = scored_data[next(iter(scored_data))]
	channels = sorted(channels_dict)

	score_matrix, backtrack_matrix = build_matrices(allowed_channels, floors, channels)
	min_hops, last_channel = get_last_channel(score_matrix, floors[-1])	
	traversed_channels = backtrack_path(backtrack_matrix, floors, last_channel)

	return min_hops, traversed_channels

def input_parser(fname='target_monsters.txt'):
	is_valid = roguard_et_parser.get_monster_name_validator()

	targets = []
	with open(fname) as f:
		# discard first line
		f.readline()

		group = set()
		for line in f:
			if not line.startswith('\n'):
				if line.startswith('#'):
					targets.append(group)
					group = set()
					continue

				name = line.strip()
				if not is_valid(name):
					print('%s is not a valid monster name.' % name)
					exit(1)
				group.add(name)

		targets.append(group)

	return targets

def display_output(et_data, min_hops, traversed_channels):
	floors = sorted(et_data)
	sep = '-' * 60

	print('\nMinimum change channels:', min_hops)
	print('\nFloor | Channel | Monsters')
	print(sep)

	for floor, channel in zip(floors, traversed_channels):
		monsters = ', '.join(et_data[floor][channel])
		print('{0:>5} | {1:^7} | {2}'.format(floor, channel, monsters))
		print(sep)

def main():
	et_data = roguard_et_parser.get_et_data()
	mvp_targets, avoid_mvp, mini_targets, extra_mini = input_parser()
	
	scored_data = et_scorer(et_data, mvp_targets, avoid_mvp,
							mini_targets, extra_mini)

	min_hops, traversed_channels = plan_channels2(scored_data)

	display_output(et_data, min_hops, traversed_channels)
	
main()
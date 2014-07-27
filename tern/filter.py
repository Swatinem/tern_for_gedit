# vim: set shiftwidth=2 tabstop=2 noexpandtab textwidth=80 wrap :

from difflib import SequenceMatcher

def filter_completions(name, completions):
	completions = list(annotate_filter(name, completions))
	completions = sorted(completions, key=lambda c: c["score"], reverse=True)

	# don’t show popup if the name is the only completion and matches exactly
	if len(completions) == 1 and completions[0]["name"] == name:
		return []

	return completions

def annotate_filter(name, completions):
	maxdepth = max(map(lambda c: c["depth"], completions)) + 1

	lenn = len(name)
	for c in completions:
		cname = c["name"]
		if lenn > len(cname):
			continue # ignore shorter completions
		# if there is no identifier, give all equal chance
		if lenn == 0:
			score = 1
			c["markup"] = cname
		else:
			m = SequenceMatcher(None, name.lower(), cname.lower())

			blocks = list(m.get_matching_blocks())

			if len(blocks) < 2:
				continue # no matches

			# run again, up to the last matching char, to have substring-scores
			last = blocks[-2]
			lastchar = last.b + last.size
			m = SequenceMatcher(None, name.lower(), cname[:lastchar].lower())

			T = lenn + lastchar
			M = 0
			for tag, i1, i2, j1, j2 in m.get_opcodes():
				# TODO: score upper/lower casing differently from normal "replace"
				if tag == "equal":
					M += i2 - i1
			if M < lenn:
				continue # not all chars are included
			score = 2.0*M / T

			# XXX: gtksourceview does not apply highlights that include the frist char
			markup = "\u200B"
			laststart = 0
			for _, start, mlen in blocks:
				markup += cname[laststart:start]
				if mlen > 0:
					markup += "<b>" + cname[start:start+mlen] + "</b>"
				laststart = start + mlen
			c["markup"] = markup

		# deeper completions should rank lower
		depth = 1 - c["depth"] / maxdepth
		c["score"] = score * depth

		yield c


from typing import List

from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry


def getEst_lenght(name: str) -> int | None:
	ests: List[HowLongToBeatEntry] = HowLongToBeat().search(
		name, similarity_case_sensitive=False
	)

	if ests:
		for est in ests:
			# TODO: Add the real est and some logic how to determine what game is meant
			return 0
			# return math.ceil(est.main_extra)
	return None

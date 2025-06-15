from typing import List, Optional

from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry


def get_est_length(name: str) -> Optional[int]:
	ests: List[HowLongToBeatEntry] = HowLongToBeat(1).search(
		name, similarity_case_sensitive=False
	)

	if ests:
		for est in ests:
			return None if est.main_extra == 0 else est.main_extra
	return None

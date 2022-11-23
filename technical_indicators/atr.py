from typing import List

def get_atr(high: List[float], low: List[float], close: List[float], period: int) -> List[float]:
  """ Returns list of ATRs with length of inputted high=low=close """
  average_true_range = [0] * (period)
  true_range = [0]
  for i in range(1, len(close)):
    true_range.append(max([high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])]))
    
  for i in range((period), len(close)):
    average_true_range.append(sum(true_range[(i - period + 1) : (i + 1)])/period)
  return average_true_range

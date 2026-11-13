# NVIDIA CEO Forecast

This model uses an adaptive sigma based on the robust scale (MAD) of the market's recent 1-minute changes (last 360 mins, floor 0.0008, cap 0.02). It widens the sigma by 1.5x if a market has experienced a large price move (>0.05) in the last 60 minutes. It uses heavy-tail quantiles (Z = [-2.0, -0.67449, 0, 0.67449, 2.0]) to better capture price jumps.

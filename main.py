import json, sys, os

# Quantile levels and Z-scores (Heavier tails)
QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
Z_HEAVY = [-2.0, -0.67449, 0, 0.67449, 2.0]

def price6(x):
    return round(min(1.0, max(0.0, x)) * 1e6) / 1e6 + 0.0

def get_robust_sigma(prices):
    # Floor raised to 0.0008
    floor = 0.0008
    if len(prices) < 2: return floor
    w = min(len(prices)-1, 360)
    diffs = [prices[i]-prices[i-1] for i in range(len(prices)-w, len(prices))]
    diffs.sort()
    med = diffs[len(diffs)//2]
    mad = sorted([abs(d - med) for d in diffs])[len(diffs)//2]
    sigma = max(floor, min(0.02, mad * 1.4826))
    return sigma

def forecast(c):
    horizon = c['horizon_minutes']
    markets = c['markets']
    
    forecasts = []
    for m in markets:
        prices = m['prices']
        last = prices[-1]
        sigma = get_robust_sigma(prices)
        
        # Jump-aware widening
        if len(prices) >= 60:
            move = abs(last - prices[-60])
            if move > 0.05:
                sigma *= 1.5
        
        rows = []
        for h in range(1, horizon + 1):
            sqh = h**0.5
            row = [price6(last + z * sigma * sqh) for z in Z_HEAVY]
            # Ensure non-decreasing
            for k in range(1, len(row)):
                if row[k] < row[k-1]: row[k] = row[k-1]
            rows.append(row)
        forecasts.append({'id': m['id'], 'q': rows})
    return forecasts

def main():
    input_dir = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for file in os.listdir(input_dir):
        if not file.endswith('.in'): continue
        
        with open(os.path.join(input_dir, file), 'r') as f:
            c = json.load(f)
            
        forecasts = forecast(c)
        
        out_path = os.path.join(output_dir, file.replace('.in', '.out'))
        with open(out_path, 'w') as f:
            json.dump({'forecasts': forecasts}, f)

if __name__ == '__main__':
    main()

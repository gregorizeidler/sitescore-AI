import argparse, os, joblib, pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--business_type', required=True, choices=['restaurante','academia','varejo_moda'])
    ap.add_argument('--segment', default=None)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    feats = ['competition','offices','schools','parks','transit','flow_kde','mix','street_centrality']
    X = df[feats]; y = df['target']
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor(random_state=42)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    print('R2:', r2_score(yte, pred)); print('MAE:', mean_absolute_error(yte, pred))
    os.makedirs(args.out, exist_ok=True)
    fname = f"{args.business_type}.joblib" if not args.segment else f"{args.business_type}_{args.segment}.joblib"
    joblib.dump(model, os.path.join(args.out, fname)); print('saved:', os.path.join(args.out, fname))

if __name__ == '__main__':
    main()

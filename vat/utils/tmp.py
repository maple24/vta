import argparse

def train_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalize", type=str, required=True, help='maximum depth')
    parser.add_argument("--n_estimators", default=100, type=int, help='number of estimators')
    parser.add_argument("--max_features", default=6, type=int, help='maximum of features',)
    parser.add_argument("--max_depth", default=5, type=int,help='maximum depth')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = train_options()
    print(opt.normalize)
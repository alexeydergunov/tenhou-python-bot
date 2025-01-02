## How to review games locally with Mortal

Tested on Ubuntu 24.04.1 LTS.

- Download https://github.com/Equim-chan/mjai-reviewer, build it as in its docs: `cargo build --release`

- Download https://github.com/Equim-chan/Mortal, copy directory Mortal/mortal from to mjai-reviewer/target/release

- Copy mortal.pth and libriichi.so (you must already have them) to mjai-reviewer/target/release/mortal

- In mjai-reviewer/target/release/mortal, copy project.example.toml to project.toml

- In mjai-reviewer/target/release/mortal, edit project.toml: `state_file = './mortal.pth'`

- Create venv in mjai-reviewer/target/release/mortal: `python3 -m venv ./venv`

- Install packages to venv: `venv/bin/pip3 install torch==2.5.1 numpy==2.2.1 tensorboard==2.18.0 tqdm==4.67.1 toml==0.10.2`

- In mjai-reviewer/target/release/mortal, `chmod +x mortal`, then modify its last line: `exec ./venv/bin/python3 mortal.py "$@"`

- In mjai-reviewer/target/release/mortal, modify mortal.py
    - This fix sets the model's tag so that it includes sha256 hash prefix and suffix of mortal.pth file:
    ```
    if 'tag' in state:
        tag = state['tag']
    else:
        import hashlib
        with open(config['control']['state_file'], 'rb') as f:
            h = hashlib.sha256(f.read()).hexdigest()
        tag = f'mortal{version}-b{num_blocks}c{conv_channels}-sha256-{h[:4]}-{h[-4:]}'
    ```

    - This is a hack for matrix in html report, we can't calculate it because we miss some files, so just fill it with zeroes:
    ```
    if review_mode:
        kyoku_cnt = len([l for l in logs if '"type":"start_kyoku"' in l])
        extra_data = {
            'model_tag': tag,
            'phi_matrix': [[[0.0, 0.0, 0.0, 0.0] for i in range(4)] for j in range(kyoku_cnt)],
        }
        print(json.dumps(extra_data), flush=True)
    ```

- Now we can run reviewer from mjai-reviewer/target/release:
`./mjai-reviewer -e mortal --show-rating -u "https://tenhou.net/0/?log=2019050417gm-0029-0000-4f2a8622&tw=2" --no-open -o _report.html --mjai-out _mjai_log.json --tenhou-out _tenhou_log.json`

- Console output:
```
$ ./mjai-reviewer -e mortal --show-rating -u "https://tenhou.net/0/?log=2019050417gm-0029-0000-4f2a8622&tw=2" --no-open -o _report.html --mjai-out _mjai_log.json --tenhou-out _tenhou_log.json
04:14:42.796656 src/main.rs:310	converting to mjai events...
04:14:42.800887 src/main.rs:345	players: カレーセット, 二宮蘭子, ⓝSuphx, 渡部惠子
04:14:42.800944 src/main.rs:346	target: ⓝSuphx (2)
04:14:45.162633 src/review/mortal.rs:248	reviewing kyoku 0, honba 0, junme 0, (0.63%)
...............
04:14:47.348076 src/review/mortal.rs:248	reviewing kyoku 1, honba 1, junme 15, (99.05%)
04:14:47.724613 src/main.rs:435	writing output...
04:14:47.770392 src/main.rs:443	complete
```

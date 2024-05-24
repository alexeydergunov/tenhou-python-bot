## How to run Mortal on Tenhou

1. Get `mortal.pth` from [shinkuan's Discord server](https://github.com/shinkuan/Akagi/blob/main/README.md#you-will-need) or from other sources.
2. Get `libriichi.so` (for Linux, exists on shinkuan's server as well) or `libriichi.pyd` (for Windows). There is an option to build it by yourself. You will need Rust compiler, then follow [the instructions on Mortal's documentation](https://mortal.ekyu.moe/user/build.html#build-and-install-libriichi).
3. Put `mortal.pth` and `libriichi.[so|pyd]` files to `project/mortal/mortal_lib`.
4. Install requirements from `requirements` folder (use `pip install -r {txt_file_path}`)
5. Run `python3 project/main.py -g {game_type} -l {lobby_id}`, where:
    - by default it goes to play a ranked match, but you can specify lobby with `-l lobby_id`,
    - `game_type` is 9 for kyu lobby, 137 for lower-dan, 41 for upper-dan, 169 for phoenix.
